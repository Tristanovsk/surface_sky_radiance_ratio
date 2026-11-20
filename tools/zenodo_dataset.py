"""
Create a DRAFT Zenodo deposition of the Rss look-up tables (dataset), with their metadata.

The draft is never published by this script: check it on the Zenodo web page, then publish it there.
Once published, copy its file URL into ``FULL_LUT_URL`` (surface_sky_radiance_ratio/main.py) and its
DOI into the README and the documentation.

Usage (from the repository root, the complete table in data/):

    export ZENODO_TOKEN=...          # personal token, scopes deposit:write and deposit:actions
    python tools/zenodo_dataset.py --sandbox      # test on https://sandbox.zenodo.org first
    python tools/zenodo_dataset.py                # real deposition

Needs ``requests``.
"""
import argparse
import hashlib
import os
import sys
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
FILES = [
    REPO / 'data' / 'surf_sky_radiance_ratio_osoaa_opac_v1.1.nc',
    REPO / 'surface_sky_radiance_ratio' / 'data' / 'surf_sky_radiance_ratio_osoaa_opac_sliced_v1.1.nc',
    REPO / 'data' / 'surf_sky_radiance_ratio_osoaa_opac_v1.nc',
]

DESCRIPTION = """
<p>Look-up tables of the surface-to-sky radiance ratio, R<sub>ss</sub>, used to convert the sky radiance
measured in above-water radiometry (AWR) into the radiance of the skylight reflected by the water surface.
R<sub>ss</sub> replaces the "sea surface reflectance factor" of Mobley (1999); it excludes the direct
sunglint and holds for clear sky conditions.</p>
<p>The values were computed with the vector (polarized) radiative transfer code OSOAA for a totally
absorbing water body, an isotropic Cox-Munk rough surface and an atmosphere of molecules (Rayleigh) and
OPAC aerosols, as described in Harmel (2023), Frontiers in Remote Sensing, 4, 1307976,
doi:10.3389/frsen.2023.1307976.</p>
<p>Dimensions of the variable <code>Rss</code> (netCDF):</p>
<ul>
<li><code>wind</code>: equivalent Cox-Munk wind speed, 0.5, 2, 4, 8, 12, 16 m s-1 (coordinate
<code>slope_variance</code>: wave slope variance)</li>
<li><code>model</code>: OPAC aerosol model at 70% relative humidity, COAV_rh70 (continental average),
DESE_rh70 (desert), MACL_rh70 (maritime clean), URBA_rh70 (urban)</li>
<li><code>aot_ref</code>: aerosol optical thickness at 550 nm, 0 to 1.5</li>
<li><code>wl</code>: wavelength, 350, 400, 500, 600, 700, 800, 1000 nm; version 1.1 adds 1600, 2200 and 2500 nm (computed without gaseous absorption: atmospheric windows only)</li>
<li><code>sza</code>: solar zenith angle, 0 to 88 degrees by step of 2</li>
<li><code>vza</code>: viewing zenith angle, 0 to 89.25 degrees (Gauss nodes)</li>
<li><code>azi</code>: relative azimuth, 0 to 360 degrees by step of 5 (0 when Sun and sensor are in
opposition)</li>
</ul>
<p>Files: <code>surf_sky_radiance_ratio_osoaa_opac_v1.1.nc</code>, complete table, 350-2500 nm;
<code>surf_sky_radiance_ratio_osoaa_opac_sliced_v1.1.nc</code>, table restricted to viewing zenith angles
30, 40 and 50 degrees and relative azimuths 45 to 160 degrees; <code>surf_sky_radiance_ratio_osoaa_opac_v1.nc</code>,
complete table of version 1.0 (350-1000 nm) as used in Harmel (2023). The values of 350-1000 nm are identical
in versions 1.0 and 1.1.</p>
<p>Python package to load and plot the tables:
<a href="https://github.com/Tristanovsk/surface_sky_radiance_ratio">surface_sky_radiance_ratio</a>.</p>
"""

METADATA = {
    'metadata': {
        'title': 'Surface-to-sky radiance ratio (Rss) look-up tables for above-water radiometry, '
                 'including polarization and aerosol effects (OSOAA, OPAC)',
        'upload_type': 'dataset',
        'description': DESCRIPTION.strip(),
        'creators': [{'name': 'Harmel, Tristan'}],
        'access_right': 'open',
        'license': 'cc-by-4.0',
        'version': '1.1',
        'keywords': ['above-water radiometry', 'surface-to-sky radiance ratio', 'sea surface reflectance factor',
                     'sky glint', 'polarization', 'aerosol', 'OSOAA', 'OPAC', 'ocean color', 'look-up table'],
        'related_identifiers': [
            {'identifier': '10.3389/frsen.2023.1307976', 'relation': 'isSupplementTo',
             'scheme': 'doi', 'resource_type': 'publication-article'},
            {'identifier': 'https://github.com/Tristanovsk/surface_sky_radiance_ratio',
             'relation': 'isSupplementedBy', 'scheme': 'url', 'resource_type': 'software'},
        ],
        'notes': 'Funding: French National Program for Remote Sensing (PNTS-2019-13).',
    }
}


def md5(path, block=2 ** 24):
    digest = hashlib.md5()
    with open(path, 'rb') as f:
        while chunk := f.read(block):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--sandbox', action='store_true', help='use https://sandbox.zenodo.org')
    args = parser.parse_args()

    token = os.environ.get('ZENODO_TOKEN')
    if not token:
        sys.exit('set the ZENODO_TOKEN environment variable')
    missing = [str(f) for f in FILES if not f.is_file()]
    if missing:
        sys.exit(f'missing files: {missing}')

    api = 'https://sandbox.zenodo.org/api' if args.sandbox else 'https://zenodo.org/api'
    headers = {'Authorization': f'Bearer {token}'}

    r = requests.post(f'{api}/deposit/depositions', json=METADATA, headers=headers, timeout=60)
    r.raise_for_status()
    deposition = r.json()
    bucket = deposition['links']['bucket']

    for path in FILES:
        print(f'uploading {path.name} ({path.stat().st_size / 1e6:.0f} MB)...')
        with open(path, 'rb') as f:
            r = requests.put(f'{bucket}/{path.name}', data=f, headers=headers, timeout=None)
        r.raise_for_status()
        if r.json()['checksum'] != f'md5:{md5(path)}':
            sys.exit(f'checksum mismatch for {path.name}')

    print(f"draft created (NOT published): {deposition['links']['html']}")
    print(f"reserved DOI: {deposition['metadata'].get('prereserve_doi', {}).get('doi')}")


if __name__ == '__main__':
    main()
