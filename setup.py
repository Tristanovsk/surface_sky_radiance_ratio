

from setuptools import setup, find_packages

__package__ = 'surface_sky_radiance_ratio'
__version__ = '1.0.0'

setup(
    name=__package__,
    version=__version__,
    packages=find_packages(exclude=['build']),
    package_data={
        '': ['*.nc', '*.txt', '*.csv', '*.dat'],

    },
    include_package_data=True,

    url='',
    license='Apache V2',
    author='T. Harmel',
    author_email='tristan.harmel@gmail.com',
    description='Minimal code to load and play with tabulated values for surface radiance correction in Above-Water Radiometry procedures',

    # Dependent packages (distributions)
    install_requires=['numpy', 'pandas', 'xarray','importlib_resources',
                      'matplotlib' ],

    # entry_points={
    #     'console_scripts': [
    #         'ssrr = TODO'
    #     ]}
)
