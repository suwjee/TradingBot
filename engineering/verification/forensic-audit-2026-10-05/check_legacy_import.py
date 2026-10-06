"""Read-only exact legacy API reproduction; failure is the audited outcome."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'package'))
# The current engine's shared modules use flat imports; provide that same
# dependency path so the wrapper reaches its own missing-export boundary.
sys.path.insert(0,str(Path(__file__).resolve().parent/'package/pipeline'))
import pipeline
