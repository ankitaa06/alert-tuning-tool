[![Documentation Status](https://readthedocs.org/projects/chembddb/badge/?version=latest)](https://chembddb.readthedocs.io/en/latest/?badge=latest)

# Alert Tuning Tool
The Alert Tuning Tool helps you understand the effect of changes in specific metrics. It allows you to query the Kusto database for scorecards.....

## Code Design:
ChemBDDB is developed in the Python 3 programming language and uses MySQL, Flask to set up a SQL database using pymysql. It uses OpenBabel and its Python extension, Pybel for handling molecules. The development follows a strictly modular and object-oriented design to make the overall code as flexible and versatile as possible. 

## Documentation:
Alert-tuning-tool documentation can be found here https://alert-tuning-tool.readthedocs.io/en/latest/index.html

## Installation and Dependencies:
General instructions:

    conda create --name alert_env python=3.7
    source activate alert_env
    conda install -c conda-forge numpy
    conda install -c conda-forge pandas
    conda install -c anaconda scipy
    pip install jupyter
    pip install -e .
