# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3", "certifi>=2025.0.0"]
# ///
"""Run bundled-script tests with their declared runtime dependencies."""
from pathlib import Path
import unittest

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parents[1] / "tests"))
    raise SystemExit(not unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful())
