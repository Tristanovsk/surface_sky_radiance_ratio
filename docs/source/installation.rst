Installation
============

surface_sky_radiance_ratio requires Python >= 3.10. Its dependencies are numpy, scipy, xarray,
netCDF4 and matplotlib (``pyproject.toml`` is the reference).

From the repository
-------------------

.. code-block:: bash

   pip install git+https://github.com/Tristanovsk/surface_sky_radiance_ratio.git

or, to run the notebooks or to develop the package, clone it first:

.. code-block:: bash

   git clone https://github.com/Tristanovsk/surface_sky_radiance_ratio.git
   cd surface_sky_radiance_ratio
   pip install ".[notebook]"
   pip install -e ".[all]"           # editable install, for development

The sliced look-up table (viewing zenith angles 30, 40 and 50 degrees, 39 MB) is installed with the
package: an editable install is not needed. The complete table (1.2 GB) is installed separately, see
:doc:`lookup_tables`.

Options
-------

The optional dependencies are grouped in extras, e.g. ``pip install ".[download,notebook]"``:

==============  ==============================================  ==========================================
extra           content                                         usage
==============  ==============================================  ==========================================
``download``    pooch                                           download of the complete table
``notebook``    JupyterLab, ipykernel, pandas, suncalc          run the notebooks of the repository
``docs``        Sphinx, sphinx-book-theme, myst-nb...           build this documentation
``test``        pytest                                          run the tests (``pytest``)
``all``         all of the above
==============  ==============================================  ==========================================

Build the documentation
-----------------------

.. code-block:: bash

   pip install -e ".[docs]"
   python -m sphinx -b html docs/source docs/build/html

The notebooks are rendered with their stored outputs, they are not executed during the build.
