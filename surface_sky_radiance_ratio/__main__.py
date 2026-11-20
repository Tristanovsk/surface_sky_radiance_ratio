"""
Command line of surface_sky_radiance_ratio.

    surface-sky-radiance-ratio path [sliced|full]   # path of a look-up table
    surface-sky-radiance-ratio download             # download the complete table (needs pooch)
    surface-sky-radiance-ratio info [sliced|full]   # dimensions and metadata of a table
"""
import argparse
import sys

from . import __version__
from .main import download, lut_file


def main(argv=None):
    parser = argparse.ArgumentParser(prog='surface-sky-radiance-ratio', description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name, help_ in [('path', 'print the path of a look-up table'),
                        ('info', 'print the dimensions and metadata of a look-up table')]:
        p = sub.add_parser(name, help=help_)
        p.add_argument('table', nargs='?', default='sliced', choices=['sliced', 'full'])
    sub.add_parser('download', help='download the complete look-up table into the shared cache')
    args = parser.parse_args(argv)

    try:
        if args.command == 'download':
            print(download())
        elif args.command == 'path':
            print(lut_file(args.table, download=False))
        else:
            import xarray as xr
            with xr.open_dataset(lut_file(args.table, download=False)) as ds:
                print(ds)
    except (FileNotFoundError, ImportError) as err:
        print(err, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
