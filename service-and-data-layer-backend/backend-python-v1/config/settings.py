# Legacy compatibility shim.
# The project uses split settings in config/settings/*.py.
# Avoid loading this file directly; it exists only to prevent accidental
# misconfiguration when another tool or environment variable points Django at
# config.settings instead of config.settings.dev.

from .settings.dev import *  # noqa: F401,F403
