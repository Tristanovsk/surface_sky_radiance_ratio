"""
Surface-to-sky radiance ratio (Rss) look-up tables for the correction of the
skylight reflected by the water surface in above-water radiometry (Harmel, 2023).
"""
from .main import lut, lut_file

__version__ = '1.1.0'

__all__ = ['lut', 'lut_file', '__version__']
