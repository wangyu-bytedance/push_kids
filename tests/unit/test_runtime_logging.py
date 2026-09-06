from __future__ import annotations

import io
import logging

from push_kids.bootstrap.app import configure_cloud_logging


def test_cloud_logging_emits_worker_info_once_without_changing_root() -> None:
    application_logger = logging.getLogger("push_kids")
    root_logger = logging.getLogger()
    original_handlers = list(application_logger.handlers)
    original_level = application_logger.level
    original_propagate = application_logger.propagate
    original_root_level = root_logger.level
    stream = io.StringIO()

    try:
        application_logger.handlers.clear()
        application_logger.setLevel(logging.NOTSET)
        application_logger.propagate = True
        root_logger.setLevel(logging.WARNING)

        configure_cloud_logging(stream)
        configure_cloud_logging(stream)
        logging.getLogger("push_kids.worker").info("worker_runtime_started")

        assert stream.getvalue().count("worker_runtime_started") == 1
        assert root_logger.level == logging.WARNING
        assert application_logger.level == logging.INFO
        assert application_logger.propagate is False
        assert len(application_logger.handlers) == 1
    finally:
        for handler in application_logger.handlers:
            if handler not in original_handlers:
                handler.close()
        application_logger.handlers[:] = original_handlers
        application_logger.setLevel(original_level)
        application_logger.propagate = original_propagate
        root_logger.setLevel(original_root_level)
