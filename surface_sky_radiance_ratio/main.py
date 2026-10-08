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

import numpy as np
import xarray as xr

import matplotlib as mpl
import matplotlib.pyplot as plt



opj = os.path.join


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
         - Wavelength :math:`\lambda` (350 to 1000)
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
    lutfile : str, optional
        Set to ``'full'`` to use the complete look-up table
        (``surf_sky_radiance_ratio_osoaa_opac_v1.nc``, about 1.2 GB, to be
        downloaded separately). By default, the sliced table shipped with the
        package is used (``surf_sky_radiance_ratio_osoaa_opac_sliced_v1.nc``),
        restricted to :math:`\theta_v` = 30, 40 and 50 degrees and
        :math:`\Delta\phi` from 45 to 160 degrees.

    Attributes
    ----------
    rss_file : str
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
    def __init__(self,lutfile=None):
        if lutfile == ('full'):
            self.rss_file = opj(os.path.dirname(__file__),'..','data','surf_sky_radiance_ratio_osoaa_opac_v1.nc')
        else:
            self.rss_file = opj(os.path.dirname(__file__), '..', 'data', 'surf_sky_radiance_ratio_osoaa_opac_sliced_v1.nc')
    def load(self):
        """
        Open the netCDF look-up table and store it in ``Rss_lut``.

        The file is opened lazily with :func:`xarray.open_dataset`.
        """
        self.Rss_lut = xr.open_dataset(self.rss_file)

    def plot_vs_sza(self,ax=None,
                    vza=40,
                    azi=90,
                    wl=500,
                    model='MACL_rh70',
                    aot_ref=0,
                    winds=[0.5,2.,4.,8,12]):
        r"""
        Plot :math:`R_{ss}` as a function of the solar zenith angle :math:`\theta_s`.

        One curve is drawn per wind speed, for a fixed viewing geometry,
        wavelength and aerosol condition.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axes to draw on, e.g., from ``fig, ax = plt.subplots(1, 1)``.
            If ``None``, a message is printed and nothing is plotted.
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
        winds : list of float, default [0.5, 2., 4., 8, 12]
            Equivalent Cox-Munk wind speeds in m s-1, linearly interpolated.
            Each wind speed is drawn as one curve.

        Returns
        -------
        matplotlib.axes.Axes or None
            The axes with the plot, or ``None`` if ``ax`` was not given.
        """

        if ax is None:
            print('please provide a matplotlib axis object, e.g., fig,ax = plt.subplots(1,1) then provide ax ')
            return
        cmap = plt.cm.Spectral_r
        norm = mpl.colors.Normalize(vmin=np.min(winds), vmax=np.max(winds))


        Rss = self.Rss_lut.Rss.sel(model=model).sel(vza=vza,azi=azi,method='nearest').interp(wl=wl)
        for i_, wind in enumerate(winds):
            color = cmap(norm(wind))
            Rss_ = Rss.interp(wind=wind).interp(aot_ref=aot_ref)
            Rss_.plot(color=color, ax=ax, label=str(wind))
        ax.text(0.05, 0.95, r'$\theta _v={:d}^\circ ,\ \Delta\phi={:d}^\circ$'.format(vza, azi),
                    size=16, transform=ax.transAxes, ha="left", va="top", )

        ax.minorticks_on()
        ax.set_title('')
        ax.set_xlim(0, 85)
        ax.legend(title=r'$Wind\ (m\cdot s^{-1})$', fontsize=12)
        ax.set_ylabel(r'$R_{ss}\ (-)$')
        ax.set_xlabel(r'$Sun\ zenith\ angle\ (deg.)$')
        return ax

    def plot_vs_vza(self,ax=None,
                    sza=40,
                    azi=90,
                    wl=500,
                    model='MACL_rh70',
                    aot_ref=0,
                    winds=[0.5,2.,4.,8,12]):
        r"""
        Plot :math:`R_{ss}` as a function of the viewing zenith angle :math:`\theta_v`.

        One curve is drawn per wind speed, for a fixed solar zenith angle,
        relative azimuth, wavelength and aerosol condition. Viewing zenith
        angles are limited to 0 to 85 degrees.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axes to draw on, e.g., from ``fig, ax = plt.subplots(1, 1)``.
            If ``None``, a message is printed and nothing is plotted.
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
        winds : list of float, default [0.5, 2., 4., 8, 12]
            Equivalent Cox-Munk wind speeds in m s-1, linearly interpolated.
            Each wind speed is drawn as one curve.

        Returns
        -------
        matplotlib.axes.Axes or None
            The axes with the plot, or ``None`` if ``ax`` was not given.
        """

        if ax is None:
            print('please provide a matplotlib axis object, e.g., fig,ax = plt.subplots(1,1) then provide ax ')
            return
        cmap = plt.cm.Spectral_r
        norm = mpl.colors.Normalize(vmin=np.min(winds), vmax=np.max(winds))


        Rss = self.Rss_lut.Rss.sel(model=model).sel(vza=slice(0,85)).sel(sza=sza,azi=azi,method='nearest').interp(wl=wl)
        for i_, wind in enumerate(winds):
            color = cmap(norm(wind))
            Rss_ = Rss.interp(wind=wind).interp(aot_ref=aot_ref)
            Rss_.plot(color=color, ax=ax, label=str(wind))
        ax.text(0.05, 0.95, r'$\theta _s={:d}^\circ ,\ \Delta\phi={:d}^\circ$'.format(sza, azi),
                    size=16, transform=ax.transAxes, ha="left", va="top", )

        ax.minorticks_on()
        ax.set_title('')
        ax.set_xlim(0, 85)
        ax.legend(title=r'$Wind\ (m\cdot s^{-1})$', fontsize=12)
        ax.set_ylabel(r'$R_{ss}\ (-)$')
        ax.set_xlabel(r'$Viewing\ zenith\ angle\ (deg.)$')
        return ax