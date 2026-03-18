"""
conftest.py — pytest configuration for DPRS.

Inserts the parent directory into sys.path so that
'from core.xxx import ...' works when pytest
is run from inside the dprs/ project root.
"""

import sys
import os

# Add the current directory (project root) to sys.path, making 'utils', 'core', etc. importable.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
