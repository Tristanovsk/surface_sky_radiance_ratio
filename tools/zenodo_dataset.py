"""
Prepare the Zenodo deposition of the Rss look-up tables (dataset), and create it as a DRAFT.

1. Stage the bundle (no network): hard links of the netCDF files, README.md and SHA256SUMS in
   data/zenodo_v<VERSION>/ :

       python tools/zenodo_dataset.py stage

2. Create the draft deposition with its metadata and upload the bundle (personal token with the
   scopes deposit:write and deposit:actions; test first on https://sandbox.zenodo.org):

       export ZENODO_TOKEN=...
       python tools/zenodo_dataset.py upload --sandbox
       python tools/zenodo_dataset.py upload

   The draft is never published by this script: check it on the Zenodo web page and publish it there.
   Then set ``ZENODO_RECORD`` (surface_sky_radiance_ratio/main.py) to the record id printed by the
   script, so that ``surface-sky-radiance-ratio download`` (and any package using
   ``surface_sky_radiance_ratio.lut_file('full')``) downloads the complete table from Zenodo, and add the
   dataset DOI to the README and the documentation.

Needs ``requests`` for the upload.
"""
import argparse
import hashlib
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from surface_sky_radiance_ratio import main as ssrr  # noqa: E402

VERSION = '1.1'
STAGE_DIR = REPO / 'data' / f'zenodo_v{VERSION}'
FILES = [
    REPO / 'data' / ssrr.FULL_LUT,
    ssrr.PACKAGE_DATA_DIR / ssrr.SLICED_LUT,
]
V1_FILE = REPO / 'data' / ssrr.FULL_LUT_V1

ARTICLE = ('Harmel, T. (2023). Apparent surface-to-sky radiance ratio of natural waters including polarization '
           'and aerosol effects: implications for above-water radiometry. Frontiers in Remote Sensing, 4, 1307976. '
           'https://doi.org/10.3389/frsen.2023.1307976')

README = f"""# Surface-to-sky radiance ratio (Rss) look-up tables for above-water radiometry

Version {VERSION}

Look-up tables of the surface-to-sky radiance ratio, Rss, used to convert the sky radiance measured in
above-water radiometry (AWR) into the radiance of the skylight reflected by the water surface:

    Rrs = (Lt - Rss * Lsky) / Ed

Rss replaces the "sea surface reflectance factor" (rho) of Mobley (1999). It excludes the direct sunglint
and holds for clear sky conditions.

## Reference

Please cite the article describing the computations:

> {ARTICLE}

## Method

Vector (polarized) radiative transfer computations with the code OSOAA (successive orders of scattering):
totally absorbing water body, isotropic Cox-Munk rough surface, atmosphere of molecules (Rayleigh,
Bodhaine et al., 1999) and OPAC aerosols (70% relative humidity, scattering matrices computed with
MOPSMAP), scale heights of 8 km (molecules) and 2 km (aerosols). Rss is the ratio of the diffuse upward
radiance just above the surface to the downward sky radiance of the specular direction.
No gaseous absorption is included.

## Files

| file | content |
|---|---|
| `{ssrr.FULL_LUT}` | complete table |
| `{ssrr.SLICED_LUT}` | viewing zenith angles 30, 40, 50 deg. (linear interpolation of the complete table), relative azimuths 45 to 160 deg. |
| `SHA256SUMS` | SHA-256 checksums of the files |

netCDF4 (compressed), variable `Rss` (float32, dimensionless) with dimensions:

| dimension | description | values | units |
|---|---|---|---|
| `wind` | equivalent Cox-Munk wind speed (coordinate `slope_variance` = 0.003 + 0.00512 wind) | 0.5, 2, 4, 8, 12, 16 | m s-1 |
| `model` | OPAC aerosol model | COAV_rh70 (continental average), DESE_rh70 (desert), MACL_rh70 (maritime clean), URBA_rh70 (urban) | - |
| `aot_ref` | aerosol optical thickness at 550 nm | 0, 0.001, 0.01, 0.1, 0.2, 0.35, 0.5, 0.7, 1, 1.5 | - |
| `wl` | wavelength (vacuum) | 350, 400, 500, 600, 700, 800, 1000, 1600, 2200, 2500 | nm |
| `sza` | solar zenith angle | 0 to 88 by step of 2 | deg. |
| `vza` | viewing zenith angle | 0 to 89.25 (Gauss nodes) | deg. |
| `azi` | relative azimuth (0 when the Sun and the sensor are in opposition) | 0 to 360 by step of 5 | deg. |

## Versions

- 1.0 (2023): tables of the article, 350-1000 nm, AOT 0 and 0.01-1.5.
- 1.1: 1.0 + wavelengths 1600, 2200, 2500 nm and AOT 0.001, from the same OSOAA computations and recipe.
  The values of version 1.0 are unchanged (bit-identical): version 1.0 is the subset wl <= 1000 nm,
  aot_ref != 0.001 of version 1.1.

## Usage notes

- Clear sky only; the direct sunglint is not included.
- No gaseous absorption: use the SWIR wavelengths (1600, 2200, 2500 nm) in atmospheric windows only, and do not
  interpolate between 1000 and 1600 nm across the 1380 nm water vapour band. 2500 nm is at the edge of strong
  absorption bands.
- For the Sun near the horizon (sza > 80 deg.) and very clear atmospheres, the sky radiance of the specular direction
  is almost nil and Rss can be large, especially in the SWIR.

## Software

Python package to load, download and plot the tables (pip installable):
https://github.com/Tristanovsk/surface_sky_radiance_ratio, documentation
https://surface-sky-radiance-ratio.readthedocs.io

```python
from surface_sky_radiance_ratio import lut
rss = lut('full')        # downloads this file once into a cache shared by all the packages
rss.load()
rss.Rss_lut.Rss.sel(model='MACL_rh70').interp(wind=4, aot_ref=0.1, sza=30, vza=40, azi=135, wl=550)
```

or with xarray only: `xarray.open_dataset('{ssrr.FULL_LUT}')`.

## License

Creative Commons Attribution 4.0 International (CC BY 4.0).

## Funding

French National Program for Remote Sensing (PNTS-2019-13).
"""

DESCRIPTION = f"""
<p>Look-up tables of the surface-to-sky radiance ratio, R<sub>ss</sub>, used to convert the sky radiance measured
in above-water radiometry (AWR) into the radiance of the skylight reflected by the water surface
(R<sub>rs</sub> = (L<sub>t</sub> - R<sub>ss</sub> L<sub>sky</sub>) / E<sub>d</sub>). R<sub>ss</sub> replaces the
"sea surface reflectance factor" of Mobley (1999); it excludes the direct sunglint and holds for clear sky.</p>
<p>Computed with the vector radiative transfer code OSOAA for a totally absorbing water body, an isotropic Cox-Munk
rough surface and an atmosphere of molecules and OPAC aerosols, as described in: {ARTICLE}</p>
<p>Dimensions of the variable <code>Rss</code> (netCDF): equivalent Cox-Munk wind speed (0.5-16 m s-1), OPAC
aerosol model (continental average, desert, maritime clean, urban, 70% relative humidity), aerosol optical
thickness at 550 nm (0-1.5), wavelength (350, 400, 500, 600, 700, 800, 1000, 1600, 2200, 2500 nm), solar zenith
angle (0-88 deg.), viewing zenith angle (0-89 deg.) and relative azimuth (0-360 deg.).</p>
<p>Version {VERSION} extends version 1.0 (the tables of the article, 350-1000 nm) with 1600, 2200 and 2500 nm and
the aerosol optical thickness 0.001, from the same computations; the values of version 1.0 are unchanged. The SWIR
values were computed without gaseous absorption: use them in atmospheric windows only. See README.md.</p>
<p>Python package to load and download the tables:
<a href="https://github.com/Tristanovsk/surface_sky_radiance_ratio">surface_sky_radiance_ratio</a>.</p>
"""

METADATA = {
    'metadata': {
        'title': 'Surface-to-sky radiance ratio (Rss) look-up tables for above-water radiometry, including '
                 'polarization and aerosol effects',
        'upload_type': 'dataset',
        'description': DESCRIPTION.strip(),
        'creators': [{'name': 'Harmel, Tristan'}],
        'access_right': 'open',
        'license': 'cc-by-4.0',
        'version': VERSION,
        'language': 'eng',
        'keywords': ['above-water radiometry', 'surface-to-sky radiance ratio', 'sea surface reflectance factor',
                     'sky glint', 'polarization', 'aerosol', 'OSOAA', 'OPAC', 'ocean color', 'look-up table'],
        'related_identifiers': [
            {'identifier': '10.3389/frsen.2023.1307976', 'relation': 'isSupplementTo',
             'scheme': 'doi', 'resource_type': 'publication-article'},
            {'identifier': 'https://github.com/Tristanovsk/surface_sky_radiance_ratio',
             'relation': 'isSupplementedBy', 'scheme': 'url', 'resource_type': 'software'},
            {'identifier': 'https://surface-sky-radiance-ratio.readthedocs.io',
             'relation': 'isDocumentedBy', 'scheme': 'url'},
        ],
        'references': [ARTICLE],
        'notes': 'Funding: French National Program for Remote Sensing (PNTS-2019-13).',
    }
}


def _digest(path, algo, block=2 ** 24):
    digest = hashlib.new(algo)
    with open(path, 'rb') as f:
        while chunk := f.read(block):
            digest.update(chunk)
    return digest.hexdigest()


def stage(with_v1=False):
    files = FILES + ([V1_FILE] if with_v1 else [])
    missing = [str(f) for f in files if not f.is_file()]
    if missing:
        sys.exit(f'missing files: {missing}')
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    for old in STAGE_DIR.iterdir():
        old.unlink()
    sums = []
    for path in files:
        target = STAGE_DIR / path.name
        try:
            os.link(path, target)           # no copy of the 1.2 GB file
        except OSError:
            import shutil
            shutil.copy2(path, target)
        sums.append(f'{_digest(target, "sha256")}  {path.name}')
        print(f'staged {path.name} ({path.stat().st_size / 1e6:.0f} MB)')
    readme = README
    if with_v1:
        readme = readme.replace('| `SHA256SUMS` |',
                                f'| `{V1_FILE.name}` | complete table of version 1.0 (350-1000 nm), as in the article |\n'
                                '| `SHA256SUMS` |')
    (STAGE_DIR / 'README.md').write_text(readme)
    (STAGE_DIR / 'SHA256SUMS').write_text('\n'.join(sums) + '\n')
    print(f'bundle ready in {STAGE_DIR}')
    print((STAGE_DIR / 'SHA256SUMS').read_text())


def upload(sandbox=False):
    import requests

    token = os.environ.get('ZENODO_TOKEN')
    if not token:
        sys.exit('set the ZENODO_TOKEN environment variable')
    if not (STAGE_DIR / 'SHA256SUMS').is_file():
        sys.exit('stage the bundle first: python tools/zenodo_dataset.py stage')
    api = 'https://sandbox.zenodo.org/api' if sandbox else 'https://zenodo.org/api'
    headers = {'Authorization': f'Bearer {token}'}

    r = requests.post(f'{api}/deposit/depositions', json=METADATA, headers=headers, timeout=60)
    r.raise_for_status()
    deposition = r.json()
    bucket = deposition['links']['bucket']
    for path in sorted(STAGE_DIR.iterdir()):
        print(f'uploading {path.name} ({path.stat().st_size / 1e6:.0f} MB)...')
        with open(path, 'rb') as f:
            r = requests.put(f'{bucket}/{path.name}', data=f, headers=headers, timeout=None)
        r.raise_for_status()
        if r.json()['checksum'] != f'md5:{_digest(path, "md5")}':
            sys.exit(f'checksum mismatch for {path.name}')

    record = deposition['id']
    print(f"\ndraft created (NOT published): {deposition['links']['html']}")
    print(f"reserved DOI: {deposition['metadata'].get('prereserve_doi', {}).get('doi')}")
    print(f"after publication, set in surface_sky_radiance_ratio/main.py:  ZENODO_RECORD = '{record}'")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('stage', help='prepare the bundle in data/zenodo_v<VERSION>/')
    p.add_argument('--with-v1', action='store_true', help=f'also include {V1_FILE.name} (version 1.0)')
    p = sub.add_parser('upload', help='create the draft deposition and upload the bundle')
    p.add_argument('--sandbox', action='store_true', help='use https://sandbox.zenodo.org')
    args = parser.parse_args()
    if args.command == 'stage':
        stage(args.with_v1)
    else:
        upload(args.sandbox)


if __name__ == '__main__':
    main()
