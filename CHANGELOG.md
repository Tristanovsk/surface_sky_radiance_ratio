# Changelog

All notable changes of surface_sky_radiance_ratio. The format follows
[Keep a Changelog](https://keepachangelog.com) and the versions follow
[Semantic Versioning](https://semver.org); each version is published from the git tag `vX.Y.Z`.

## [Unreleased]

## [1.1.0] - 2026-11-20

Look-up tables v1.1 extended to 350-2500 nm, and packaging following current best practices: the package works when installed from a wheel (no editable
install needed), tests and continuous integration, documentation in the style of the other projects.

### Added (look-up tables)

- Look-up tables v1.1: wavelengths 1600, 2200 and 2500 nm added to 350-1000 nm, from the same OSOAA
  computations (`boa_lut_opac_wind_updown_v2.nc`) and recipe as v1.0, whose values are kept unchanged.
- Look-up tables v1.1: aerosol optical thickness 0.001 added for all the wavelengths (simulated for
  Harmel, 2023, and listed in its Table 4, but not kept in v1.0).
  Computed without gaseous absorption: atmospheric windows only. Global attributes (title, references,
  license, conventions), compressed float32 netCDF. Built by `tools/make_lut_v1_1.py`.
- `lut()` uses the sliced table v1.1 (installed with the package); `lut('full')` uses the complete table v1.1,
  or the v1.0 file with a warning when v1.1 is not found.
- Tutorial on the SWIR wavelengths; the getting started and optimal geometries tutorials rewritten and
  documented.

### Changed

- The sliced look-up table moved from `data/` into the package (`surface_sky_radiance_ratio/data/`), so
  that `pip install .` (not only `pip install -e .`) finds it.
- `lut('full')` searches the complete table in the folder given by the environment variable
  `SURFACE_SKY_RADIANCE_RATIO_DATA`, then in the `data/` folder of the repository clone, then in the
  cache of the package, where it can be downloaded with `pooch` (`[download]` extra) once its Zenodo
  record is published. `lut()` also accepts the path of a netCDF file.
- `lut.plot_vs_sza` / `lut.plot_vs_vza` create a figure when no `ax` is given (instead of printing a
  message and returning `None`); the label shows the tabulated angles actually used.
- `lut.load()` returns the dataset and passes its keyword arguments to `xarray.open_dataset`.
- `pyproject.toml`: version read from `surface_sky_radiance_ratio.__version__`, SPDX license,
  classifiers, URLs, lower bounds of the dependencies, extras `download`, `notebook`, `docs`, `test`,
  `all`. Python >= 3.10.

### Fixed

- `scipy` added to the dependencies (needed by the `.interp` of xarray used in the plots and the examples).
- `plot_vs_sza` / `plot_vs_vza` failed with `ValueError` when the fixed angles were given as floats
  (format `{:d}` of the label).
- Mutable default argument `winds=[...]` replaced by a tuple.

### Added

- `surface_sky_radiance_ratio.__version__` and `lut_file()`.
- Tests on the sliced table (`tests/`), GitHub Actions workflows `ci.yml` (build, tests of the installed
  wheel on Python 3.10-3.13, docs build) and `publish.yml` (PyPI with Trusted Publishing, GitHub release).
- `CHANGELOG.md`, `CITATION.cff`, `.zenodo.json` (GitHub-Zenodo archiving of the releases) and
  `tools/zenodo_dataset.py` (draft Zenodo deposition of the look-up tables).
- Documentation: installation, look-up tables and changelog pages, API pages generated per object, logo.

## [1.0.0] - 2023-12-21

First version, published with Harmel (2023), Frontiers in Remote Sensing, 4, 1307976,
doi:10.3389/frsen.2023.1307976.

[Unreleased]: https://github.com/Tristanovsk/surface_sky_radiance_ratio/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/Tristanovsk/surface_sky_radiance_ratio/releases/tag/v1.1.0
[1.0.0]: https://github.com/Tristanovsk/surface_sky_radiance_ratio/tree/6a30380
