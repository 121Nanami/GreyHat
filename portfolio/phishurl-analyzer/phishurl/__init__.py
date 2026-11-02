"""phishurl — offline phishing URL analyzer (defensive)."""

from .analyze import Finding, Report, analyze

__all__ = ["Finding", "Report", "analyze"]
__version__ = "0.1.0"
