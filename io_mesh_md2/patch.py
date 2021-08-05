import os
import sys


def add_local_modules_to_path():
    """Add local modules directory to system path. This is done so the
    addon can find it's dependencies."""
    modules_dir = os.path.join(os.path.dirname(__file__), 'modules')
    modules_dir = os.path.abspath(modules_dir)

    if not modules_dir in sys.path:
        sys.path.append(modules_dir)
