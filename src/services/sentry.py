import os
import sentry_sdk
import logging

from sentry_sdk.integrations.logging import LoggingIntegration
from dotenv import load_dotenv

load_dotenv()

sentry_url = os.getenv("SENTRY_URL")

sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.ERROR,
)


sentry_sdk.init(
    dsn=sentry_url,
    integrations=[sentry_logging],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)
