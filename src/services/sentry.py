import sentry_sdk
import logging

from sentry_sdk.integrations.logging import LoggingIntegration

from src.conf.config import settings


sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.ERROR,
)


sentry_sdk.init(
    dsn=settings.sentry_url,
    integrations=[sentry_logging],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)
