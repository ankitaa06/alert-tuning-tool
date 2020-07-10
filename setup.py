import setuptools
from os import path
import alert

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

if __name__ == "__main__":
    setuptools.setup(
        name='Alert Tuning Tool',
        version='0.1',
        author='Ankita Agrawal',
        author_email='ankagr@microsoft.com',
        project_urls={
            'Source': 'https://github.com/hachmannlab/chemml',
            'url': 'https://hachmannlab.github.io/chemml/'
        },
        description=
        'desc',
        long_description=long_description,
        long_description_content_type="text/markdown",
        keywords=[
            'Alert', 'Tuning',
            'Tool'
        ],
        license='BSD-3C',
        packages=setuptools.find_packages(),
        include_package_data=True,

        install_requires=[
            'numpy', 'pandas', 'scipy','jupyter'
        ],
        extras_require={
            'docs': [
                'sphinx',
                'sphinxcontrib-napoleon',
                'sphinx_rtd_theme',
                'numpydoc',
                'nbsphinx'
            ],
            'tests': [
                'pytest',
                'pytest-cov',
                'pytest-pep8',
                'tox'
            ],
        },
        tests_require=[
            'pytest',
            'pytest-cov',
            'pytest-pep8',
            'tox',
        ],
        zip_safe=False,
    )
