ISIMIP quality assessment
=========================

[![Latest release](https://shields.io/github/v/release/ISI-MIP/isimip-qa)](https://github.com/ISI-MIP/isimip-qa/releases)
[![Python Version: 3.6|3.7|3.8|3.9|3.10](https://img.shields.io/badge/python-3.6|3.7|3.8|3.9|3.10-blue)](https://www.python.org/)
[![License: MIT](http://img.shields.io/badge/license-MIT-yellow.svg)](https://github.com/ISI-MIP/isimip-qa/blob/master/LICENSE)

A command line tool to for quality assessment whithin the ISIMIP project.

Using ISIMIP datasets in NetCDF format as input, the tool creates (a) extractions of the data as CSV files using predefined regions or points, and (b) creates plots to assess the data from these regions.

**This is still work in progress.**


Setup
-----

The application is written in Python (> 3.6) uses only dependencies, which can be installed without administrator priviledges. The installation of Python (and its developing packages), however differs from operating system to operating system. Optional Git is needed if the application is installed directly from GitHub. The installation of Python 3 and Git for different plattforms is documented [here](https://github.com/ISI-MIP/isimip-utils/blob/master/docs/prerequisites.md).

The tool itself can be installed via pip. Usually you want to create a [virtual environment](https://docs.python.org/3/library/venv.html) first, but this is optional.

```bash
# setup venv on Linux/macOS/Windows WSL
python3 -m venv env
source env/bin/activate

# setup venv on Windows cmd
python -m venv env
call env\Scripts\activate.bat

# install directly from GitHub
pip install git+https://github.com/ISI-MIP/isimip-qa@dev

# update from Github
pip install --upgrade git+https://github.com/ISI-MIP/isimip-qa@dev
```

Usage
-----

The tool has several options which can be inspected using the help option `-h, --help`:

```bash
usage: isimip-qa [-h] [--config-file CONFIG_FILE] [--datasets-path DATASETS_PATH]
                 [--extractions-path EXTRACTIONS_PATH] [--assessments-path ASSESSMENTS_PATH]
                 [-e EXTRACTIONS] [-a ASSESSMENTS] [-r REGIONS] [-g {0,1,2}] [-f] [-l]
                 [--extractions-only] [--assessments-only] [--times TIMES] [--vmin VMIN]
                 [--vmax VMAX] [--cmap CMAP] [--protocol-location PROTOCOL_LOCATIONS]
                 [--log-level LOG_LEVEL] [--log-file LOG_FILE]
                 path [specifiers ...]

positional arguments:
  path                  Path of the dataset to process
  specifiers            Specifiers in the from identifier=specifier1,specifier2,...

optional arguments:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE
                        File path of the config file
  --datasets-path DATASETS_PATH
                        base path for the input datasets
  --extractions-path EXTRACTIONS_PATH
                        base path for the output extractions
  --assessments-path ASSESSMENTS_PATH
                        base path for the output assessments
  -e EXTRACTIONS, --extractions EXTRACTIONS
                        Run only specific extractions (comma seperated)
  -a ASSESSMENTS, --assessments ASSESSMENTS
                        Run only specific assessments (comma seperated)
  -r REGIONS, --regions REGIONS
                        extract only specific regions (comma seperated)
  -g {0,1,2}, --grid {0,1,2}
                        Maximum dimensions of the plot grid [default: 2]
  -f, --force           Always run extractions
  -l, --load            Load NetCDF datasets completely in memory
  --extractions-only    Run only assessments
  --assessments-only    Run only assessments
  --times TIMES         Time steps to use for maps (comma seperated)
  --vmin VMIN           Fixed minimal colormap value for maps.
  --vmax VMAX           Fixed maximum colormap value for maps.
  --cmap CMAP           Colormap to use for maps.
  --protocol-location PROTOCOL_LOCATIONS
                        URL or file path to the protocol
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file
```

The only mandatory argument is the path to an ISIMIP dataset, relative to the `DATASETS_PATH`, e.g. `ISIMIP3b/OutputData/water_global/CWatM/gfdl-esm4/historical/cwatm_gfdl-esm4_w5e5_historical_histsoc_default_qtot_global_daily`.

It makes sense to set at least `DATASETS_PATH` (location the NetCDF input files), `EXTRACTIONS_PATH` (location of the csv extractions), and `ASSESSMENTS_PATH` (location of the plots) to different directories, either by command line options or by a config file (in `isimip.conf` in the same directory, `~/.isimip.conf`, or `/etc/isimip.conf`):

```
[isimip-qa]
datasets_path = ~/data/isimip/qa/datasets
extractions_path = ~/data/isimip/qa/extractions
assessments_path = ~/data/isimip/qa/assessments

log_level = INFO
```

All other command line options can be set in the config file as well.

Datasets can be parametrized by the sytax:

```
isimip-qc path/to/dataset <identifier>=<specifier1>,<specifier2>,...
```

E.g.

```
ISIMIP3b/OutputData/water_global/CWatM/gfdl-esm4/historical/cwatm_gfdl-esm4_w5e5_historical_histsoc_default_qtot_global_daily model=CWatM,H08
```

would process

```
ISIMIP3b/OutputData/water_global/CWatM/gfdl-esm4/historical/cwatm_gfdl-esm4_w5e5_historical_histsoc_default_qtot_global_daily
ISIMIP3b/OutputData/water_global/H08/gfdl-esm4/historical/h08_gfdl-esm4_w5e5_historical_histsoc_default_qtot_global_daily
```

Multiple identifier/specifier combinations can be used to create a grid of combinations.
