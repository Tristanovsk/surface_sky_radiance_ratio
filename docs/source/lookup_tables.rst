Look-up tables
==============

:math:`R_{ss}` is tabulated in netCDF files, opened with :mod:`xarray` by :meth:`lut.load
<surface_sky_radiance_ratio.main.lut.load>`. The variable ``Rss`` has the dimensions
``(wind, model, aot_ref, wl, sza, vza, azi)``:

.. rst-class:: wrap

=============  ===============================================  ====================================  =========
dimension      description                                      values                                units
=============  ===============================================  ====================================  =========
``wind``       equivalent Cox-Munk wind speed                   0.5, 2, 4, 8, 12, 16                  m s-1
``model``      OPAC aerosol model (70% relative humidity)       COAV_rh70, DESE_rh70, MACL_rh70,      \-
                                                                URBA_rh70
``aot_ref``    aerosol optical thickness at 550 nm              0, 0.01, 0.1, 0.2, 0.35, 0.5, 0.7,    \-
                                                                1, 1.5; v1.1: 0.001
``wl``         wavelength                                       350, 400, 500, 600, 700, 800, 1000;   nm
                                                                v1.1: 1600, 2200, 2500
``sza``        solar zenith angle                               0 to 88 by step of 2                  degrees
``vza``        viewing zenith angle                             full: 0 to 89.25 (Gauss nodes);       degrees
                                                                sliced: 30, 40, 50
``azi``        relative azimuth (0: Sun and sensor in           full: 0 to 360 by step of 5;          degrees
               opposition)                                      sliced: 45 to 160 by step of 5
=============  ===============================================  ====================================  =========

Versions
--------

=========  ==============  =======================================================================
version    wavelengths     content
=========  ==============  =======================================================================
1.0        350-1000 nm     tables of Harmel (2023)
1.1        350-2500 nm     1.0 (values unchanged) + 1600, 2200 and 2500 nm and AOT 0.001 (simulated
                           but not kept in 1.0) from the same OSOAA computations and recipe; global
                           metadata; compressed netCDF
=========  ==============  =======================================================================

.. warning::

   The radiative transfer computations do not include the gaseous absorption. Use the SWIR values
   (1600, 2200, 2500 nm) in the atmospheric windows only, and do not interpolate between 1000 and
   1600 nm across the 1380 nm water vapour band (see :doc:`tutorials/swir_extension`).

The table is rebuilt from the OSOAA up/down radiance look-up table by ``tools/make_lut_v1_1.py``.

The coordinate ``slope_variance`` gives the wave slope variance :math:`\sigma^2` of the isotropic
Cox-Munk model attached to each ``wind``. The values hold for clear sky conditions and exclude the
direct sunglint (see :doc:`theory`).

Sliced table
------------

``surf_sky_radiance_ratio_osoaa_opac_sliced_v1.1.nc`` is installed with the package and loaded by
default:

.. code-block:: python

   from surface_sky_radiance_ratio import lut

   rss = lut()
   rss.load()
   rss.Rss_lut.Rss.sel(model='MACL_rh70', vza=40, azi=135).interp(wind=4, aot_ref=0.1, sza=30, wl=550)

Complete table
--------------

``surf_sky_radiance_ratio_osoaa_opac_v1.1.nc`` (about 1.2 GB) covers all the viewing directions. Load it
with ``lut('full')``, which searches it, in order:

1. in the folder given by the environment variable ``SURFACE_SKY_RADIANCE_RATIO_DATA``,
2. in the ``data`` folder of a clone of the repository,
3. in the cache of the package (:func:`pooch.os_cache`), where it is downloaded (with
   ``pip install ".[download]"``) from its Zenodo record.

Until then, place it in one of the first two folders. If only the version 1.0 file
(``surf_sky_radiance_ratio_osoaa_opac_v1.nc``, link in the README) is found, it is used with a warning. Any other netCDF file with the same structure can be given by path: ``lut('/path/to/file.nc')``.

Use in other packages
---------------------

Other packages (e.g. aqua3cs) can rely on surface_sky_radiance_ratio to get the tables instead of shipping
their own copy. Declare the dependency in their ``pyproject.toml``:

.. code-block:: toml

   dependencies = ["surface_sky_radiance_ratio[download]"]

and get the path of a table:

.. code-block:: python

   import xarray as xr
   from surface_sky_radiance_ratio import lut_file

   sliced = xr.open_dataset(lut_file())          # installed with the package
   full = xr.open_dataset(lut_file('full'))      # downloaded once from Zenodo, then read from the cache

The complete table is downloaded only once per machine into the cache of the package
(:func:`pooch.os_cache`, e.g. ``~/.cache/surface_sky_radiance_ratio`` on Linux), whatever the package or the
environment (pip, conda, venv) that asks for it, and checked with its SHA-256 checksum. It can be downloaded
beforehand from the command line:

.. code-block:: bash

   surface-sky-radiance-ratio download           # complete table into the shared cache
   surface-sky-radiance-ratio path full          # where it is
   surface-sky-radiance-ratio info               # dimensions and metadata of the sliced table

In a conda environment, install the package with pip (``pip install surface_sky_radiance_ratio[download]``)
after the conda packages. To use a copy of the table already on the machine, set
``SURFACE_SKY_RADIANCE_RATIO_DATA`` to its folder.

.. note::

   With the SWIR wavelengths of version 1.1, a spectral interpolation over the whole table changes slightly
   with a cubic method between 350 and 1000 nm (the spline also passes through 1600-2500 nm). To reproduce
   version 1.0 results, select ``wl <= 1000`` before a cubic interpolation, or use a linear interpolation.

Citation
--------

If you use the look-up tables, please cite:

   Harmel, T. (2023). Apparent surface-to-sky radiance ratio of natural waters including
   polarization and aerosol effects: implications for above-water radiometry. *Frontiers in Remote
   Sensing*, 4, 1307976. https://doi.org/10.3389/frsen.2023.1307976

The citation metadata of the package are given in ``CITATION.cff``.
