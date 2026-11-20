'''
Generate the light and dark mode versions of the README / documentation figures.

Run from the repository root:

    python illustration/make_illustrations.py

Figures are saved with a transparent background so that they blend with any
light (resp. dark) page background.
'''

from pathlib import Path

import colorsys

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from surface_sky_radiance_ratio import lut

ILLUSTRATION_DIR = Path(__file__).resolve().parent

THEMES = {
    'light': {'fg': '#24292f', 'legend_bg': 'white'},
    'dark': {'fg': '#e6edf3', 'legend_bg': '#161b22'},
}


def plot_rss_vs_sza(theme):
    '''Rss vs. sun zenith angle for two relative azimuths (sliced look-up table).'''
    colors = THEMES[theme]
    rc = {
        'axes.labelsize': 18, 'font.size': 16, 'legend.fontsize': 12,
        'xtick.labelsize': 16, 'ytick.labelsize': 16,
        'font.family': 'serif', 'mathtext.fontset': 'stix',
        'text.color': colors['fg'], 'axes.labelcolor': colors['fg'],
        'axes.edgecolor': colors['fg'],
        'xtick.color': colors['fg'], 'ytick.color': colors['fg'],
        'legend.facecolor': colors['legend_bg'], 'legend.edgecolor': colors['fg'],
        'savefig.transparent': True,
    }
    with plt.rc_context(rc):
        rss = lut()
        rss.load()
        fig, axs = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
        for ax, azi in zip(axs, [90, 135]):
            rss.plot_vs_sza(ax=ax, vza=40, azi=azi, wl=500, model='MACL_rh70', aot_ref=0)
        axs[1].set_ylabel(r'$R_{ss}\ (-)$')
        fig.suptitle('wl=500.0, aot=0.000, model=MACL_rh70')
        fig.tight_layout()
        fig.savefig(ILLUSTRATION_DIR / f'Rss_Rayleigh_500nm_vza40_{theme}.png', dpi=100)
        plt.close(fig)


def white_to_alpha(rgb):
    '''Make the white background transparent ("color to alpha").

    Each pixel is seen as an opaque color blended over white; alpha is the
    smallest opacity reproducing the observed pixel.
    '''
    rgb = rgb.astype(float) / 255
    alpha = 1 - rgb.min(axis=-1)
    with np.errstate(divide='ignore', invalid='ignore'):
        color = 1 - (1 - rgb) / alpha[..., None]
    color = np.where(alpha[..., None] > 0, color, 0)
    return np.clip(color, 0, 1), alpha


def invert_lightness(color):
    '''Invert the lightness of RGB colors while keeping hue and saturation.'''
    hls = np.apply_along_axis(lambda c: colorsys.rgb_to_hls(*c), -1, color)
    hls[..., 1] = 1 - hls[..., 1]
    return np.apply_along_axis(lambda c: colorsys.hls_to_rgb(*c), -1, hls)


def viewing_geometry(theme):
    '''Viewing geometry figure (Fig. 1 of Harmel, 2023) on a transparent background.'''
    rgb = np.asarray(Image.open(ILLUSTRATION_DIR / 'viewing_geometry.jpg').convert('RGB'))
    color, alpha = white_to_alpha(rgb)
    if theme == 'dark':
        color = invert_lightness(color)
    rgba = np.dstack([color, alpha])
    Image.fromarray((rgba * 255).round().astype(np.uint8), 'RGBA').save(
        ILLUSTRATION_DIR / f'viewing_geometry_{theme}.png')


if __name__ == '__main__':
    for theme in THEMES:
        plot_rss_vs_sza(theme)
        viewing_geometry(theme)
