"""Tests on the sliced look-up table shipped with the package."""
import matplotlib

matplotlib.use('Agg')

import numpy as np  # noqa: E402
import pytest  # noqa: E402

import surface_sky_radiance_ratio as ssrr  # noqa: E402
from surface_sky_radiance_ratio import lut, lut_file  # noqa: E402
from surface_sky_radiance_ratio import main  # noqa: E402

DIMS = ('wind', 'model', 'aot_ref', 'wl', 'sza', 'vza', 'azi')


@pytest.fixture(scope='module')
def rss():
    table = lut()
    table.load()
    yield table
    table.Rss_lut.close()


def test_version():
    assert isinstance(ssrr.__version__, str)


def test_sliced_table_is_packaged():
    path = lut_file()
    assert path.is_file()
    assert path.parent.name == 'data'
    assert path.parent.parent.name == 'surface_sky_radiance_ratio'


def test_structure(rss):
    ds = rss.Rss_lut
    assert ds.Rss.dims == DIMS
    assert list(ds.vza.values) == [30, 40, 50]
    assert set(ds.model.values) == {'COAV_rh70', 'DESE_rh70', 'MACL_rh70', 'URBA_rh70'}
    assert list(ds.wl.values) == [350, 400, 500, 600, 700, 800, 1000, 1600, 2200, 2500]
    assert 'slope_variance' in ds.coords


def test_values_are_physical(rss):
    assert bool(np.isfinite(rss.Rss_lut.Rss).all())
    Rss = rss.Rss_lut.Rss.sel(model='MACL_rh70', aot_ref=0.1, vza=40, azi=135, sza=30)
    # Fresnel reflectance of a flat surface at 40 degrees is about 0.025
    assert np.all((Rss > 0.01) & (Rss < 0.1))


def test_interpolation(rss):
    value = rss.Rss_lut.Rss.sel(model='MACL_rh70', vza=40, azi=135).interp(
        wind=4, aot_ref=0.1, sza=30, wl=550)
    assert value.ndim == 0
    assert 0.01 < float(value) < 0.1


@pytest.mark.parametrize('method, kwargs', [
    ('plot_vs_sza', {'vza': 40.0, 'azi': 135}),
    ('plot_vs_vza', {'sza': 30, 'azi': 90.0}),
])
def test_plots(rss, method, kwargs):
    ax = getattr(rss, method)(**kwargs)    # no axes given: a figure is created
    assert len(ax.lines) == 5
    matplotlib.pyplot.close('all')


def test_custom_path(tmp_path):
    with pytest.raises(FileNotFoundError):
        lut_file(tmp_path / 'missing.nc')
    assert lut_file(str(lut_file())) == lut_file()


def test_full_table_not_found(tmp_path, monkeypatch):
    monkeypatch.setattr(main, 'REPO_DATA_DIR', tmp_path)
    monkeypatch.setattr(main, '_cache_dir', lambda: None)
    monkeypatch.delenv(main.DATA_DIR_ENV, raising=False)
    with pytest.raises(FileNotFoundError, match=main.FULL_LUT):
        lut_file('full', download=False)


def test_full_table_from_env(tmp_path, monkeypatch):
    (tmp_path / main.FULL_LUT).write_bytes(b'')
    monkeypatch.setenv(main.DATA_DIR_ENV, str(tmp_path))
    assert lut_file('full') == tmp_path / main.FULL_LUT


def test_full_table_falls_back_to_v1(tmp_path, monkeypatch):
    (tmp_path / main.FULL_LUT_V1).write_bytes(b'')
    monkeypatch.setenv(main.DATA_DIR_ENV, str(tmp_path))
    monkeypatch.setattr(main, 'REPO_DATA_DIR', tmp_path / 'none')
    monkeypatch.setattr(main, '_cache_dir', lambda: None)
    with pytest.warns(UserWarning, match='version 1.0'):
        assert lut_file('full') == tmp_path / main.FULL_LUT_V1
