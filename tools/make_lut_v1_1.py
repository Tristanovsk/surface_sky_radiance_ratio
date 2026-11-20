"""
Build the v1.1 look-up tables of Rss (350-2500 nm) from the v1 table and the OSOAA up/down LUT.

v1.1 = v1 (350, 400, 500, 600, 700, 800, 1000 nm, values unchanged) + 1600, 2200 and 2500 nm computed
with the same recipe as v1, i.e. the ratio of the upward radiance just above the surface (vza < 90)
to the downward sky radiance of the specular direction (180 - vza), from the OSOAA runs of
boa_lut_opac_wind_updown_v2.nc (water body totally absorbing, sunglint not included in the radiance
field, see Harmel, 2023). As in v1, the aerosol optical thickness 0.001 is not kept.

Recomputing the v1 wavelengths with this recipe gives the v1 values to a relative difference
< 6e-5 (float32 rounding of the intermediate computations): the v1 values are kept as published.

Usage (from the repository root):

    python tools/make_lut_v1_1.py \
        --updown /data/vrtc/xlut/boa_lut_opac_wind_updown_v2.nc \
        --v1 data/surf_sky_radiance_ratio_osoaa_opac_v1.nc \
        --outdir data

writes surf_sky_radiance_ratio_osoaa_opac_v1.1.nc (complete) and
surf_sky_radiance_ratio_osoaa_opac_sliced_v1.1.nc (vza = 30, 40, 50 degrees, azi = 45 to 160 degrees).
"""
import argparse
import datetime
from pathlib import Path

import numpy as np
import xarray as xr

SWIR_WL = [1600., 2200., 2500.]
VERSION = '1.1'

GLOBAL_ATTRS = {
    'title': 'Surface-to-sky radiance ratio (Rss) for above-water radiometry, including polarization '
             'and aerosol effects',
    'summary': 'Ratio of the diffuse radiance reflected by the rough water surface to the sky radiance of '
               'the specular direction, computed with the vector radiative transfer code OSOAA for a '
               'totally absorbing water body, an isotropic Cox-Munk surface and the OPAC aerosol models '
               '(70% relative humidity). Clear sky; direct sunglint excluded.',
    'version': VERSION,
    'creator_name': 'Tristan Harmel',
    'references': 'Harmel, T. (2023). Apparent surface-to-sky radiance ratio of natural waters including '
                  'polarization and aerosol effects: implications for above-water radiometry. Frontiers in '
                  'Remote Sensing, 4, 1307976. https://doi.org/10.3389/frsen.2023.1307976',
    'source': 'OSOAA vector radiative transfer computations (successive orders of scattering)',
    'license': 'CC-BY-4.0',
    'Conventions': 'CF-1.8',
    'comment': 'Wavelengths 350-1000 nm are the values of version 1.0. Wavelengths 1600, 2200 and 2500 nm '
               '(added in version 1.1) were computed without gaseous absorption: use them in atmospheric '
               'windows only; 2500 nm is at the edge of strong water vapour and methane absorption.',
    'software': 'https://github.com/Tristanovsk/surface_sky_radiance_ratio',
}


def swir_rss(updown_file):
    """Rss at SWIR_WL from the up/down radiance LUT (same recipe as v1)."""
    xlut = xr.open_dataset(updown_file, chunks={'model': 1, 'wind': 1, 'aot_ref': 1})
    xlut['wl'] = xlut['wl'] * 1000
    xlut = xlut.sel(wl=SWIR_WL).drop_isel(aot_ref=1)        # drop aot_ref = 0.001, as in v1
    Id = xlut.I.sel(vza=slice(90.001, 180.001))
    Iu = xlut.I.sel(vza=slice(0, 90))
    Id['vza'] = 180 - Id['vza']
    Id = Id.sortby('vza')
    Id['vza'] = Iu['vza']
    return (Iu / Id).astype('float32')


def encoding(ds):
    chunks = tuple(1 if d in ('wind', 'model', 'aot_ref', 'wl') else ds.sizes[d] for d in ds.Rss.dims)
    return {'Rss': {'zlib': True, 'complevel': 4, 'shuffle': True, 'chunksizes': chunks,
                    'dtype': 'float32', '_FillValue': np.float32(np.nan)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--updown', required=True, help='OSOAA up/down radiance LUT (boa_lut_opac_wind_updown_v2.nc)')
    parser.add_argument('--v1', required=True, help='complete Rss table v1 (surf_sky_radiance_ratio_osoaa_opac_v1.nc)')
    parser.add_argument('--outdir', default='data')
    args = parser.parse_args()
    outdir = Path(args.outdir)

    v1 = xr.open_dataset(args.v1, chunks={'model': 1, 'wind': 1, 'aot_ref': 1})
    swir = swir_rss(args.updown)
    # same coordinates as v1 (float rounding of the angles and AOT of the up/down LUT)
    for dim in ('aot_ref', 'sza', 'vza', 'azi', 'wind'):
        np.testing.assert_allclose(swir[dim].values, v1[dim].values, atol=1e-3, err_msg=dim)
    assert list(swir.model.values) == list(v1.model.values)
    swir = swir.assign_coords({d: v1[d] for d in ('aot_ref', 'sza', 'vza', 'azi', 'wind')})
    swir = swir.transpose(*v1.Rss.dims)

    Rss = xr.concat([v1.Rss, swir], dim='wl', coords='minimal', compat='override')
    Rss.attrs = dict(v1.Rss.attrs, version=VERSION)
    Rss.attrs['reference'] = GLOBAL_ATTRS['references']
    ds = Rss.to_dataset(name='Rss')
    for coord in ds.coords:
        if coord in v1.coords:
            ds[coord].attrs = v1[coord].attrs
    ds['wl'].attrs = v1['wl'].attrs
    ds.attrs = dict(GLOBAL_ATTRS, date_created=datetime.date.today().isoformat())

    full = outdir / f'surf_sky_radiance_ratio_osoaa_opac_v{VERSION}.nc'
    print(f'writing {full}')
    ds.to_netcdf(full, encoding=encoding(ds))

    # sliced table: as for v1, linear interpolation to vza = 30, 40, 50 and azi = 45 to 160
    full_ds = xr.open_dataset(full)
    sliced = full_ds.sel(azi=slice(45, 160)).interp(vza=[30, 40, 50])
    sliced['Rss'] = sliced.Rss.astype('float32')
    sliced['vza'].attrs = {'units': 'degrees', 'long_name': 'viewing_zenith_angle'}
    sliced.attrs['comment'] = (GLOBAL_ATTRS['comment'] + ' Sliced table: viewing zenith angles 30, 40 and 50 '
                               'degrees (linear interpolation of the complete table) and relative azimuths '
                               '45 to 160 degrees.')
    out = outdir / f'surf_sky_radiance_ratio_osoaa_opac_sliced_v{VERSION}.nc'
    print(f'writing {out}')
    sliced.load().to_netcdf(out, encoding=encoding(sliced))


if __name__ == '__main__':
    main()
