"""Fixed extraction, consolidation and history matching with recoverable stage DTOs."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from functools import partial
from hashlib import sha256
from pathlib import Path
from time import monotonic
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel, ValidationError

from push_kids.agent_processing.checkpoints import StageCheckpoints, fingerprint
from push_kids.agent_processing.contracts import (
    AnalysisInput,
    AnalysisProposal,
    ModelAnalysisResult,
    ModelEvidenceReference,
    ModelLearningItem,
    _has_runtime_uncertainty,
    _model_summary_errors,
    explicit_same_day_review,
)
from push_kids.agent_processing.coverage import propose_coverage
from push_kids.agent_processing.failures import StageFailure
from push_kids.agent_processing.history_search import HistorySearchRequest
from push_kids.agent_processing.stage_contracts import (
    EXTRACT_INSTRUCTIONS,
    MATCH_INSTRUCTIONS,
    MERGE_INSTRUCTIONS,
    PIPELINE_REVISION,
    ConsolidatedResult,
    ExtractedPoint,
    MatchingResult,
    MaterialResult,
)
from push_kids.agent_processing.stage_io import stage_io
from push_kids.agent_processing.telemetry import AnalysisTrace
from push_kids.knowledge.normalization import normalize_knowledge_name

T = TypeVar("T", bound=BaseModel)


class StageProvider(Protocol):
    concurrency: int
    parameter_revision: str

    async def generate_stage(
        self,
        stage: str,
        instructions: str,
        payload: dict[str, Any],
        schema: type[BaseModel],
        images: list[tuple[str, Path]],
        deadline: float,
        trace: AnalysisTrace,
    ) -> BaseModel: ...


class StagedPipeline:
    def __init__(
        self,
        provider: StageProvider,
        trace: AnalysisTrace,
        checkpoints: StageCheckpoints | None = None,
    ):
        self.provider, self.trace, self.checkpoints = provider, trace, checkpoints
        self.calls = 0
        self._checkpoint_lock = asyncio.Lock()

    async def _call(
        self,
        stage: str,
        unit: str,
        instructions: str,
        payload: dict[str, Any],
        schema: type[T],
        images: list[tuple[str, Path]],
        deadline: float,
        validate: Callable[[T], None],
        cache_input: object = None,
    ) -> T:
        digest = fingerprint(
            {
                "revision": PIPELINE_REVISION,
                "parameters": self.provider.parameter_revision,
                "payload": payload,
                "context": cache_input,
                "images": [(alias, sha256(p.read_bytes()).hexdigest()) for alias, p in images],
            }
        )
        cached = self.checkpoints.get(unit, digest) if self.checkpoints else None
        if cached is not None:
            try:
                value = schema.model_validate(cached)
                validate(value)
                self.trace.info(
                    "analysis_stage_cache",
                    stage=stage,
                    unit=unit,
                    revision=PIPELINE_REVISION,
                    checkpoint_hit=True,
                )
                return value
            except (ValueError, StageFailure):
                pass
        stage_deadline = min(deadline, monotonic() + (45 if stage in {"extract", "group"} else 30))
        for correction in range(1 if stage in {"extract", "group"} else 2):
            if stage_deadline <= monotonic():
                raise StageFailure("local_deadline")
            self.calls += 1
            if self.calls > 16:
                raise StageFailure("capacity", retryable=False)
            try:
                async with asyncio.timeout(max(0.001, stage_deadline - monotonic())):
                    response = await self.provider.generate_stage(
                        stage,
                        instructions,
                        payload,
                        schema,
                        images,
                        stage_deadline,
                        self.trace,
                    )
                value = schema.model_validate(response.model_dump())
                validate(value)
                if self.checkpoints:
                    async with self._checkpoint_lock:
                        await stage_io(
                            partial(
                                self.checkpoints.put,
                                unit,
                                digest,
                                value.model_dump(),
                                deadline=deadline,
                            ),
                            deadline,
                        )
                return value
            except TimeoutError:
                self.trace.warning(
                    "analysis_stage_failed",
                    stage=stage,
                    unit=unit,
                    revision=PIPELINE_REVISION,
                    reason="local_deadline",
                )
                raise StageFailure("local_deadline", stage=stage, unit=unit) from None
            except (ValidationError, StageFailure) as exc:
                reason = exc.reason if isinstance(exc, StageFailure) else "validation"
                self.trace.warning(
                    "analysis_stage_failed",
                    stage=stage,
                    unit=unit,
                    revision=PIPELINE_REVISION,
                    reason=reason,
                )
                if (
                    stage in {"extract", "group"}
                    or correction
                    or reason not in {"validation", "coverage"}
                ):
                    raise StageFailure(
                        reason,
                        retryable=getattr(exc, "retryable", True),
                        retry_after=getattr(exc, "retry_after", 0),
                        stage=stage,
                        unit=unit,
                    ) from None
                payload = {**payload, "correction": reason}
        raise StageFailure("validation")

    @staticmethod
    def _validate_material(value: MaterialResult, aliases: set[str], subjects: set[str]) -> None:
        if value.status == "unreadable":
            raise StageFailure("unreadable")
        if (value.status == "content" and not value.items and not value.needs_context) or (
            value.status != "content" and value.items
        ):
            raise StageFailure("coverage")
        for item in value.items:
            if item.subject not in subjects or not set(item.materials) <= aliases:
                raise StageFailure("validation")
            if not item.name.strip() or not item.evidence.strip():
                raise StageFailure("validation")

    async def run(
        self,
        data: AnalysisInput,
        search: Callable[[HistorySearchRequest], list[dict]],
        deadline: float,
    ) -> AnalysisProposal:
        self.calls = 0
        subjects = set(data.allowed_analysis_subjects())
        if not subjects or len(data.image_paths) > 9 or not (data.image_paths or data.text):
            raise StageFailure("input", retryable=False)
        materials: dict[str, Path] = {}
        hashes: set[str] = set()
        for index, path in enumerate(data.image_paths, 1):
            digest = sha256(path.read_bytes()).hexdigest()
            if digest not in hashes:
                materials[f"m{index}"] = path
                hashes.add(digest)
        common = {"subjects": sorted(subjects), "grade": data.grade, "parent_text": data.text}
        semaphore = asyncio.Semaphore(self.provider.concurrency)
        extraction_deadline = min(deadline, monotonic() + 180)

        async def extract(alias: str, path: Path | None) -> tuple[str, MaterialResult]:
            async with semaphore:
                aliases = {alias}
                result = await self._call(
                    "extract",
                    alias,
                    EXTRACT_INSTRUCTIONS,
                    {**common, "materials": [alias]},
                    MaterialResult,
                    [(alias, path)] if path is not None else [],
                    extraction_deadline,
                    lambda value: self._validate_material(value, aliases, subjects),
                )
                return alias, result

        tasks = [asyncio.create_task(extract(a, p)) for a, p in materials.items()]
        if data.text and data.text.strip():
            tasks.append(asyncio.create_task(extract("t", None)))
        try:
            # Keep independent successful units even when another fails.
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except BaseException:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            raise
        for result in results:
            if isinstance(result, BaseException):
                raise result
        extracted = dict(result for result in results if isinstance(result, tuple))
        pending = [a for a, r in extracted.items() if r.needs_context]
        groups: list[set[str]] = []
        ordered = list(materials)
        for alias in pending:
            if alias == "t":
                group = set(ordered[:3]) | {"t"}
            else:
                index = ordered.index(alias)
                group = set(ordered[max(0, index - 1) : index + 2])
                if "t" in extracted:
                    group.add("t")
            if len(group - {"t"}) > 3 or len(group) < 2:
                raise StageFailure("coverage")
            if not any(group <= existing for existing in groups):
                groups.append(group)
        if len(groups) > 2:
            raise StageFailure("capacity")
        for index, group in enumerate(groups):

            def validate_group(value: MaterialResult, aliases: set[str] = group) -> None:
                self._validate_material(value, aliases, subjects)
                if value.needs_context:
                    raise StageFailure("coverage")
                unresolved = {a for a in aliases if extracted[a].needs_context}
                covered = {a for item in value.items for a in item.materials}
                if not unresolved <= covered:
                    raise StageFailure("coverage")

            enriched = await self._call(
                "group",
                f"group{index}",
                EXTRACT_INSTRUCTIONS,
                {
                    **common,
                    "materials": sorted(group),
                    "required_materials": sorted(a for a in group if extracted[a].needs_context),
                    "excerpts": {a: extracted[a].excerpt for a in group},
                },
                MaterialResult,
                [(a, materials[a]) for a in sorted(group) if a in materials],
                deadline,
                validate_group,
            )
            # Keep already identified units; consolidation accounts for all candidates.
            extracted[f"group{index}"] = enriched
        candidates: dict[str, ExtractedPoint] = {}
        seen: set[str] = set()
        for material_result in extracted.values():
            for extracted_item in material_result.items:
                digest = fingerprint(extracted_item.model_dump())
                if digest not in seen:
                    seen.add(digest)
                    candidates[f"c{len(candidates) + 1}"] = extracted_item
        if not candidates or len(candidates) > 200:
            raise StageFailure("coverage" if not candidates else "capacity")

        def validate_merge(value: ConsolidatedResult) -> None:
            if _model_summary_errors(value.summary) or _has_runtime_uncertainty(
                value.uncertainties
            ):
                raise StageFailure("validation")
            members = [m for item in value.items for m in item.members]
            identities = [
                (item.subject, normalize_knowledge_name(item.name)) for item in value.items
            ]
            if len(identities) != len(set(identities)):
                raise StageFailure("validation")
            if len(members) != len(set(members)) or set(members) != set(candidates):
                raise StageFailure("coverage")
            for item in value.items:
                if (
                    not normalize_knowledge_name(item.name)
                    or not item.category.strip()
                    or not item.review_method.strip()
                ):
                    raise StageFailure("validation")
                if any(candidates[m].subject != item.subject for m in item.members):
                    raise StageFailure("validation")

        merged = await self._call(
            "merge",
            "merge",
            MERGE_INSTRUCTIONS,
            {"candidates": {k: v.model_dump() for k, v in candidates.items()}},
            ConsolidatedResult,
            [],
            deadline,
            validate_merge,
        )

        # Owner executes every required query; the model cannot skip or alter it.
        options: dict[str, dict[str, Any]] = {}
        decision_inputs = []
        for index, item in enumerate(merged.items):
            request = HistorySearchRequest(
                candidate_key=item.name,
                subject_name=item.subject,
                keywords=(item.name[:40],),
            )
            await stage_io(partial(search, request), deadline)
            candidate_options: dict[str, Any] = {}
            for known in data.same_day_learning:
                if known.subject_name == item.subject:
                    candidate_options[f"s{len(candidate_options)}"] = {
                        "kind": "same_day",
                        "name": known.name,
                        "value": known,
                    }
            for known_review in data.review_candidates().values():
                if known_review.subject_name == item.subject:
                    candidate_options[f"h{len(candidate_options)}"] = {
                        "kind": known_review.match_kind,
                        "name": known_review.knowledge_name,
                        "value": known_review,
                    }
            if len(candidate_options) > 320:
                raise StageFailure("capacity")
            alias = f"i{index}"
            options[alias] = candidate_options
            decision_inputs.append(
                {
                    "candidate": alias,
                    "subject": item.subject,
                    "name": item.name,
                    "options": [
                        {"id": k, "kind": v["kind"], "name": v["name"]}
                        for k, v in candidate_options.items()
                    ],
                }
            )

        def validate_matches(value: MatchingResult) -> None:
            aliases = [d.candidate for d in value.decisions]
            if len(aliases) != len(set(aliases)) or set(aliases) != set(options):
                raise StageFailure("coverage")
            for choice in value.decisions:
                if choice.uncertain:
                    raise StageFailure("validation")
                if choice.match is not None and choice.match not in options[choice.candidate]:
                    raise StageFailure("validation")

        matched = await self._call(
            "match",
            "match",
            MATCH_INSTRUCTIONS,
            {"candidates": decision_inputs},
            MatchingResult,
            [],
            deadline,
            validate_matches,
            cache_input={
                k: {a: v["value"].model_dump() for a, v in choices.items()}
                for k, choices in options.items()
            },
        )
        decisions = {d.candidate: d for d in matched.decisions}
        final: dict[str, list[ModelLearningItem]] = {s: [] for s in subjects}
        uncertainties = list(merged.uncertainties)
        for index, item in enumerate(merged.items):
            alias = f"i{index}"
            decision = decisions[alias]
            exact = [
                v
                for v in options[alias].values()
                if normalize_knowledge_name(v["name"]) == normalize_knowledge_name(item.name)
            ]
            chosen = options[alias].get(decision.match or "")
            if exact:
                chosen = exact[0]
            if chosen and chosen["kind"] == "same_day":
                if not explicit_same_day_review(data.text):
                    uncertainties.append(f"{item.name}当天已确认，已省略重复材料。")
                    continue
                same_day_id = chosen["value"].knowledge_id
                chosen = next(
                    (
                        v
                        for v in options[alias].values()
                        if v["kind"] != "same_day"
                        and v["value"].knowledge_id == chosen["value"].knowledge_id
                    ),
                    None,
                )
                if chosen is None:
                    await stage_io(
                        partial(
                            search,
                            HistorySearchRequest(
                                candidate_key=item.name,
                                subject_name=item.subject,
                                keywords=(item.name[:40],),
                                knowledge_id=same_day_id,
                            ),
                        ),
                        deadline,
                    )
                    resolved = next(
                        (
                            r
                            for r in data.review_candidates().values()
                            if r.knowledge_id == same_day_id
                        ),
                        None,
                    )
                    if resolved is None:
                        raise StageFailure("validation")
                    chosen = {"kind": resolved.match_kind, "value": resolved}
            evidence: list[ModelEvidenceReference] = []
            confidence = "high"
            for member in item.members:
                point = candidates[member]
                if point.confidence == "low" or confidence == "low":
                    confidence = "low"
                elif point.confidence == "medium":
                    confidence = "medium"
                for source in point.materials:
                    ref = ModelEvidenceReference(
                        source="parent_text" if source == "t" else "image",
                        image_index=None if source == "t" else int(source[1:]),
                        detail=point.evidence,
                    )
                    if ref not in evidence:
                        evidence.append(ref)
            if len(evidence) > 20:
                raise StageFailure("capacity")
            matched_review = chosen["value"] if chosen else None
            final[item.subject].append(
                ModelLearningItem(
                    kind=chosen["kind"] if chosen else "new",
                    name=matched_review.knowledge_name if matched_review else item.name,
                    review_id=matched_review.review_id if matched_review else None,
                    existing_knowledge_id=matched_review.knowledge_id if matched_review else None,
                    category=item.category,
                    display_kind=item.display_kind,
                    review_method=item.review_method,
                    estimated_minutes=item.estimated_minutes,
                    direct_evidence=evidence,
                    context_used=[],
                    confidence=confidence,
                )
            )
        # Distinct extracted names can resolve to one canonical history item. Preserve
        # every source before the public validator deduplicates review identities.
        for subject, items in final.items():
            unique: dict[tuple[str, str], ModelLearningItem] = {}
            for assembled in items:
                key = (
                    assembled.kind,
                    assembled.existing_knowledge_id or normalize_knowledge_name(assembled.name),
                )
                if key not in unique:
                    unique[key] = assembled
                else:
                    kept = unique[key]
                    kept.direct_evidence.extend(
                        e for e in assembled.direct_evidence if e not in kept.direct_evidence
                    )
                    if len(kept.direct_evidence) > 20:
                        raise StageFailure("capacity")
            final[subject] = list(unique.values())
        proposal = data.validate_model_result(
            ModelAnalysisResult(
                summary=merged.summary,
                source="图片记录" if materials else "手动记录",
                subjects=final,
                uncertainties=uncertainties[:20],
            )
        )
        await propose_coverage(
            self.provider, proposal, data.existing_knowledge, deadline, self.trace
        )
        return proposal
