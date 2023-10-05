import os

import numpy as np
import xarray as xr

import matplotlib as mpl
import matplotlib.pyplot as plt



opj = os.path.join


class lut():
    def __init__(self):
        self.rss_file = opj(os.path.dirname(__file__),'..','data','surf_sky_radiance_ratio_osoaa_opac_v1.nc')

    def load(self):
        self.Rss_lut = xr.open_dataset(self.rss_file)

    def plot_vs_sza(self,ax=None,
                    vza=40,
                    azi=90,
                    wl=500,
                    model='MACL_rh70',
                    aot_ref=0,
                    winds=[0.5,2.,4.,8,12]):

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
        ax.legend(title='$Wind\ (m\cdot s^{-1})$', fontsize=12)
        ax.set_ylabel('$R_{ss}\ (-)$')
        ax.set_xlabel('$Sun\ zenith\ angle\ (deg.)$')
        return ax

