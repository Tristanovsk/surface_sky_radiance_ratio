r"""
Surface-to-sky radiance ratio (:math:`R_{ss}`) look-up table.

Look-up table of the surface-to-sky radiance ratio used to correct the
skylight reflected by the water surface in above-water radiometry (AWR)
(Harmel, 2023).

The radiance measured by a sensor pointing down at the water is

.. math::

    L_t(\theta_s, \theta_v, \Delta\phi, \lambda) =
    L_w(\theta_s, \theta_v, \Delta\phi, \lambda) +
    L_{surf}(\theta_s, \theta_v, \Delta\phi, \lambda)

where :math:`L_w` is the water-leaving radiance and :math:`L_{surf}` is the
radiance reflected by the air-water interface. The surface term splits into
a diffuse (sky) component and a direct (sunglint) component:

.. math::

    L_{surf} = L_{surf}^{diff} + L_{surf}^{dir}

The surface-to-sky radiance ratio relates the diffuse surface radiance to
the sky radiance measured in the direction that a flat surface would
reflect specularly towards the sensor:

.. math::

    R_{ss}(\theta_s, \theta_v, \Delta\phi, \lambda) =
    \frac{L_{surf}^{diff}(\theta_s, \theta_v, \Delta\phi, \lambda)}
         {L_{sky}(\theta_s, \pi - \theta_v, \Delta\phi, \lambda)}

:math:`R_{ss}` replaces the sea surface reflectance factor
:math:`\rho_{Mobley}` (Mobley, 1999). It is a ratio of two radiances, not a
true reflectance. Once :math:`L_{surf}^{dir}` (sunglint) has been removed
separately, the remote sensing reflectance follows as

.. math::

    R_{rs} = \frac{L_t - R_{ss} \, L_{sky}}{E_d}

where :math:`E_d` is the downwelling irradiance just above the surface.

The tabulated values were computed with the vector radiative transfer code
OSOAA for a totally absorbing water body (:math:`L_w = 0`), a Cox-Munk
isotropic rough surface and the OPAC aerosol models. They hold for clear
sky conditions and exclude the direct sunglint component.

References
----------
Harmel, T. (2023). Apparent surface-to-sky radiance ratio of natural waters
including polarization and aerosol effects: implications for above-water
radiometry. *Frontiers in Remote Sensing*, 4, 1307976.
https://doi.org/10.3389/frsen.2023.1307976

Mobley, C. D. (1999). Estimation of the remote-sensing reflectance from
above-surface measurements. *Applied Optics*, 38(36), 7442-7455.
"""
import os
import warnings
from pathlib import Path

import numpy as np
import xarray as xr

__all__ = ['lut', 'lut_file', 'SLICED_LUT', 'FULL_LUT', 'FULL_LUT_V1', 'FULL_LUT_URL']

#: Folder of the look-up table shipped with the package.
PACKAGE_DATA_DIR = Path(__file__).resolve().parent / 'data'
#: ``data`` folder of a clone of the repository (former location of the tables).
REPO_DATA_DIR = Path(__file__).resolve().parents[1] / 'data'

#: Sliced look-up table shipped with the package (vza = 30, 40, 50 degrees, 350-2500 nm).
SLICED_LUT = 'surf_sky_radiance_ratio_osoaa_opac_sliced_v1.1.nc'
#: Complete look-up table (350-2500 nm), downloaded separately.
FULL_LUT = 'surf_sky_radiance_ratio_osoaa_opac_v1.1.nc'
#: Download URL of the complete look-up table (Zenodo record, None until it is published).
FULL_LUT_URL = None
#: SHA-256 checksum of the complete look-up table, checked after download.
FULL_LUT_SHA256 = 'f6fe457ef1430c7dcf8337201ad9ca9b9577b94bc51eaa537f7d9fa8266c1317'
#: Complete look-up table of version 1.0 (350-1000 nm, Harmel 2023), used if v1.1 is not found.
FULL_LUT_V1 = 'surf_sky_radiance_ratio_osoaa_opac_v1.nc'
#: Location of the complete look-up table of version 1.0.
FULL_LUT_GDRIVE = 'https://drive.google.com/file/d/1rJ9RkGhNj3jEk3qmS6oGV8VdZaRzL5bO/view?usp=sharing'

#: Environment variable giving a folder that holds the complete look-up table.
DATA_DIR_ENV = 'SURFACE_SKY_RADIANCE_RATIO_DATA'


def _cache_dir():
    try:
        import pooch
    except ImportError:
        return None
    return Path(pooch.os_cache('surface_sky_radiance_ratio'))


def lut_file(lutfile=None, download=True):
    """
    Path of a look-up table file.

    Parameters
    ----------
    lutfile : str or path-like, optional
        ``None`` or ``'sliced'`` for the sliced table shipped with the package,
        ``'full'`` for the complete table, or the path of a netCDF file.
    download : bool, default True
        For ``'full'``: download the table into the local cache when it is not
        found locally (needs ``pooch``, ``pip install "surface_sky_radiance_ratio[download]"``).

    Returns
    -------
    pathlib.Path
        Path of the netCDF file.

    Raises
    ------
    FileNotFoundError
        If the file is not found (and cannot be downloaded).

    Notes
    -----
    The complete table is searched, in order, in the folder given by the
    environment variable ``SURFACE_SKY_RADIANCE_RATIO_DATA``, in the ``data``
    folder of the repository clone and in the cache of the package
    (:func:`pooch.os_cache`).
    """
    if lutfile is None or lutfile == 'sliced':
        return PACKAGE_DATA_DIR / SLICED_LUT
    if lutfile != 'full':
        path = Path(lutfile).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f'look-up table not found: {path}')
        return path

    candidates = []
    if os.environ.get(DATA_DIR_ENV):
        candidates.append(Path(os.environ[DATA_DIR_ENV]).expanduser())
    candidates.append(REPO_DATA_DIR)
    cache = _cache_dir()
    if cache is not None:
        candidates.append(cache)
    for folder in candidates:
        if (folder / FULL_LUT).is_file():
            return folder / FULL_LUT
    for folder in candidates:
        if (folder / FULL_LUT_V1).is_file():
            warnings.warn(f'{FULL_LUT} not found, using {FULL_LUT_V1} (version 1.0, 350-1000 nm)',
                          stacklevel=2)
            return folder / FULL_LUT_V1

    if download and FULL_LUT_URL is not None:
        try:
            import pooch
        except ImportError as err:
            raise ImportError('pooch is needed to download the complete look-up table: '
                              'pip install "surface_sky_radiance_ratio[download]"') from err
        known_hash = f'sha256:{FULL_LUT_SHA256}' if FULL_LUT_SHA256 else None
        return Path(pooch.retrieve(FULL_LUT_URL, known_hash=known_hash, fname=FULL_LUT,
                                   path=cache, progressbar=True))

    searched = ', '.join(str(f) for f in candidates)
    if FULL_LUT_URL is not None:
        hint = f'Download it from {FULL_LUT_URL}'
    else:
        hint = f'Download it (or {FULL_LUT_V1}, version 1.0, from {FULL_LUT_GDRIVE})'
    raise FileNotFoundError(
        f'{FULL_LUT} not found (searched: {searched}). {hint} '
        f'and place it in one of these folders, or set {DATA_DIR_ENV} to its folder.')


class lut():
    r"""
    Load and plot the tabulated surface-to-sky radiance ratio :math:`R_{ss}`.

    The look-up table is stored as a netCDF file. Once it is loaded with
    :meth:`load`, it is available as the :class:`xarray.Dataset`
    ``Rss_lut``. Its variable ``Rss`` has the dimensions below.

    .. list-table::
       :header-rows: 1
       :widths: 15 65 20

       * - Dimension
         - Description
         - Units
       * - ``wind``
         - Equivalent Cox-Munk wind speed (0.5 to 16)
         - m s-1
       * - ``model``
         - OPAC aerosol model at 70% relative humidity: ``COAV_rh70``
           (continental average), ``DESE_rh70`` (desert), ``MACL_rh70``
           (maritime clean), ``URBA_rh70`` (urban)
         - --
       * - ``aot_ref``
         - Aerosol optical thickness at 550 nm (0 to 1.5)
         - --
       * - ``wl``
         - Wavelength :math:`\lambda` (350 to 1000, and 1600, 2200, 2500
           since version 1.1)
         - nm
       * - ``sza``
         - Solar zenith angle :math:`\theta_s` (0 to 88, step 2)
         - degrees
       * - ``vza``
         - Viewing zenith angle :math:`\theta_v`
         - degrees
       * - ``azi``
         - Relative azimuth :math:`\Delta\phi`, equal to 0 when the Sun and
           sensor are in opposition
         - degrees

    The wave slope variance :math:`\sigma^2` of the isotropic Cox-Munk
    model is stored as the coordinate ``slope_variance``, attached to
    ``wind``.

    Parameters
    ----------
    lutfile : str or path-like, optional
        By default, the sliced table shipped with the package is used
        (``surf_sky_radiance_ratio_osoaa_opac_sliced_v1.1.nc``), restricted to
        :math:`\theta_v` = 30, 40 and 50 degrees and :math:`\Delta\phi` from
        45 to 160 degrees. Set to ``'full'`` to use the complete look-up table
        (``surf_sky_radiance_ratio_osoaa_opac_v1.1.nc``, to be
        downloaded separately, see :func:`lut_file`), or give the path of a
        netCDF file.

    Attributes
    ----------
    rss_file : pathlib.Path
        Path of the netCDF look-up table file.
    Rss_lut : xarray.Dataset
        The look-up table. Only set after :meth:`load` is called.

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> from surface_sky_radiance_ratio import lut
    >>> rss = lut()
    >>> rss.load()
    >>> rss.Rss_lut.Rss.sel(model='MACL_rh70', vza=40, azi=135).interp(
    ...     wind=4, aot_ref=0.1, sza=30, wl=550)
    >>> fig, ax = plt.subplots(1, 1)
    >>> rss.plot_vs_sza(ax=ax, vza=40, azi=135)
    """

    def __init__(self, lutfile=None):
        self.rss_file = lut_file(lutfile)

    def load(self, **kwargs):
        """
        Open the netCDF look-up table and store it in ``Rss_lut``.

        The file is opened lazily with :func:`xarray.open_dataset`.

        Parameters
        ----------
        **kwargs
            Passed to :func:`xarray.open_dataset` (e.g. ``chunks={}`` to use dask).

        Returns
        -------
        xarray.Dataset
            The look-up table (also stored in ``Rss_lut``).
        """
        self.Rss_lut = xr.open_dataset(self.rss_file, **kwargs)
        return self.Rss_lut

    def _plot_winds(self, Rss, ax, winds, aot_ref, xname, label):
        import matplotlib as mpl
        import matplotlib.pyplot as plt

        if ax is None:
            _, ax = plt.subplots(1, 1)
        cmap = plt.cm.Spectral_r
        norm = mpl.colors.Normalize(vmin=np.min(winds), vmax=np.max(winds))
        for wind in winds:
            Rss.interp(wind=wind, aot_ref=aot_ref).plot(color=cmap(norm(wind)), ax=ax, label=f'{wind:g}')
        ax.text(0.05, 0.95, label, size=16, transform=ax.transAxes, ha='left', va='top')
        ax.minorticks_on()
        ax.set_title('')
        ax.set_xlim(0, 85)
        ax.legend(title=r'$Wind\ (m\cdot s^{-1})$', fontsize=12)
        ax.set_ylabel(r'$R_{ss}\ (-)$')
        ax.set_xlabel(xname)
        return ax

    def plot_vs_sza(self, ax=None,
                    vza=40,
                    azi=90,
                    wl=500,
                    model='MACL_rh70',
                    aot_ref=0,
                    winds=(0.5, 2., 4., 8, 12)):
        r"""
        Plot :math:`R_{ss}` as a function of the solar zenith angle :math:`\theta_s`.

        One curve is drawn per wind speed, for a fixed viewing geometry,
        wavelength and aerosol condition.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Axes to draw on. If ``None``, a new figure is created.
        vza : float, default 40
            Viewing zenith angle :math:`\theta_v` in degrees. The nearest
            tabulated value is used.
        azi : float, default 90
            Relative azimuth :math:`\Delta\phi` in degrees (0 when the Sun and
            sensor are in opposition). The nearest tabulated value is used.
        wl : float, default 500
            Wavelength :math:`\lambda` in nm, linearly interpolated.
        model : str, default 'MACL_rh70'
            OPAC aerosol model: ``'COAV_rh70'``, ``'DESE_rh70'``,
            ``'MACL_rh70'`` or ``'URBA_rh70'``.
        aot_ref : float, default 0
            Aerosol optical thickness at 550 nm, linearly interpolated.
        winds : sequence of float, default (0.5, 2., 4., 8, 12)
            Equivalent Cox-Munk wind speeds in m s-1, linearly interpolated.
            Each wind speed is drawn as one curve.

        Returns
        -------
        matplotlib.axes.Axes
            The axes with the plot.
        """
        Rss = self.Rss_lut.Rss.sel(model=model).sel(vza=vza, azi=azi, method='nearest').interp(wl=wl)
        label = r'$\theta _v={:g}^\circ ,\ \Delta\phi={:g}^\circ$'.format(
            float(Rss.vza), float(Rss.azi))
        return self._plot_winds(Rss, ax, winds, aot_ref, r'$Sun\ zenith\ angle\ (deg.)$', label)

    def plot_vs_vza(self, ax=None,
                    sza=40,
                    azi=90,
                    wl=500,
                    model='MACL_rh70',
                    aot_ref=0,
                    winds=(0.5, 2., 4., 8, 12)):
        r"""
        Plot :math:`R_{ss}` as a function of the viewing zenith angle :math:`\theta_v`.

        One curve is drawn per wind speed, for a fixed solar zenith angle,
        relative azimuth, wavelength and aerosol condition. Viewing zenith
        angles are limited to 0 to 85 degrees.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Axes to draw on. If ``None``, a new figure is created.
        sza : float, default 40
            Solar zenith angle :math:`\theta_s` in degrees. The nearest
            tabulated value is used.
        azi : float, default 90
            Relative azimuth :math:`\Delta\phi` in degrees (0 when the Sun and
            sensor are in opposition). The nearest tabulated value is used.
        wl : float, default 500
            Wavelength :math:`\lambda` in nm, linearly interpolated.
        model : str, default 'MACL_rh70'
            OPAC aerosol model: ``'COAV_rh70'``, ``'DESE_rh70'``,
            ``'MACL_rh70'`` or ``'URBA_rh70'``.
        aot_ref : float, default 0
            Aerosol optical thickness at 550 nm, linearly interpolated.
        winds : sequence of float, default (0.5, 2., 4., 8, 12)
            Equivalent Cox-Munk wind speeds in m s-1, linearly interpolated.
            Each wind speed is drawn as one curve.

        Returns
        -------
        matplotlib.axes.Axes
            The axes with the plot.
        """
        Rss = self.Rss_lut.Rss.sel(model=model).sel(vza=slice(0, 85)).sel(
            sza=sza, azi=azi, method='nearest').interp(wl=wl)
        label = r'$\theta _s={:g}^\circ ,\ \Delta\phi={:g}^\circ$'.format(
            float(Rss.sza), float(Rss.azi))
        return self._plot_winds(Rss, ax, winds, aot_ref, r'$Viewing\ zenith\ angle\ (deg.)$', label)
