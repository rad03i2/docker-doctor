"""Docker Doctor: static diagnostics for Docker project files."""

__version__ = "1.0.0"
__author__ = "Radwan Abdulhadi Ahmed (@rad03i2)"

from .scanner import Finding, Report, scan_project

__all__ = ["Finding", "Report", "scan_project"]