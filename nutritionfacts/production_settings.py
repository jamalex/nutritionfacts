import os

from .settings import *

DEBUG = False

TELEMETRY_SENTRY_DSN = os.getenv("TELEMETRY_SENTRY_DSN")

if TELEMETRY_SENTRY_DSN:

    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=TELEMETRY_SENTRY_DSN,
        integrations=[DjangoIntegration()],
        environment=os.getenv("TELEMETRY_SENTRY_ENVIRONMENT") or "unknown",
    )
