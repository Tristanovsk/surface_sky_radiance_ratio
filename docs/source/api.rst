.. _api:

API reference
=============

The look-up table class and the file helper are importable from the package itself:

.. code-block:: python

   from surface_sky_radiance_ratio import lut, lut_file

   rss = lut()                  # sliced table shipped with the package
   ds = rss.load()              # xarray.Dataset, variable "Rss"
   rss_full = lut('full')       # complete table (see the look-up tables page)

Look-up table
-------------

.. autosummary::
   :toctree: generated
   :template: autosummary/class.rst
   :nosignatures:

   surface_sky_radiance_ratio.main.lut

Files
-----

.. autosummary::
   :toctree: generated
   :nosignatures:

   surface_sky_radiance_ratio.main.lut_file

Module overview
---------------

.. automodule:: surface_sky_radiance_ratio.main
   :no-members:
   :no-index:
