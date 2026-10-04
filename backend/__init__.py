"""Backend package with its directory available as the import root."""

import sys
from pathlib import Path

BACKEND_DIR = str(Path(__file__).resolve().parent)
if BACKEND_DIR not in sys.path:
	sys.path.insert(0, BACKEND_DIR)
