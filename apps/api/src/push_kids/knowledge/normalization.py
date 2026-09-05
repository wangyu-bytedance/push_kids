import re
import unicodedata


def normalize_knowledge_name(name: str) -> str:
    value = unicodedata.normalize("NFKC", name).strip().lower()
    value = re.sub(r"[\s，。！？、；：,.!?;:（）()\[\]]+", "", value)
    return value[:140]
