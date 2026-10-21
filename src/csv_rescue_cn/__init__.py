"""csv-rescue-cn: fix garbled CSV files from legacy Chinese systems."""
from .core import ConvertStats, convert_file, detect_encoding

__version__ = "0.1.0"
__all__ = ["ConvertStats", "convert_file", "detect_encoding", "__version__"]
