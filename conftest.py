"""
pytest configuration - root conftest.py

Excludes script-style files that are meant to be run directly (not via pytest)
and configures pytest-asyncio settings.
"""

# Exclude legacy script-style "test" files that use print-based verification
# (not real pytest tests - they run module-level code at import time)
collect_ignore = [
    "framework/test_components.py",
    "framework/test_fix.py",
]
