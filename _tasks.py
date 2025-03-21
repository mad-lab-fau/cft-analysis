import platform
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent


def task_docs():
    """Build the html docs using Sphinx."""
    if platform.system() == "Windows":
        return subprocess.run([HERE / "docs/make.bat", "html"])
    else:
        return subprocess.run(["make", "-C", HERE / "docs", "html"])