"""Redis-backed processing worker for deployment environments."""

import json
import logging
import redis

from backend.core.config import settings
from backend.schemas.job import JobCreateRequest
from backend.services.pipeline_service import pipeline_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AvalancheVision.Worker")


def run() -> None:
    if not settings.REDIS_URL:
        raise RuntimeError("REDIS_URL must be configured for the worker.")
    queue = redis.from_url(settings.REDIS_URL, decode_responses=True)
    logger.info("Waiting for pipeline jobs")
    while True:
        _, payload = queue.blpop("avalanchevision:pipeline")
        message = json.loads(payload)
        request = JobCreateRequest.model_validate(message["request"])
        pipeline_service._execute_pipeline(message["job_id"], request)


if __name__ == "__main__":
    run()