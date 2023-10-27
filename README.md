ISIMIP quality assessment
=========================

[![Python Version](https://img.shields.io/badge/python->=3.8-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/ISI-MIP/isimip-qc/blob/master/LICENSE)

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
pip install git+https://github.com/ISI-MIP/isimip-qa

# update from Github
pip install --upgrade git+https://github.com/ISI-MIP/isimip-qa
```

Usage
-----

The tool has several options which can be inspected using the help option `-h, --help`:

```bash
usage: isimip-qa [-h] [--datasets-path DATASETS_PATH] [--extractions-path EXTRACTIONS_PATH]
                 [--plots-path PLOTS_PATH] [-e EXTRACTIONS] [-a PLOTS] [-r REGIONS] [-p PERIODS]
                 [-g {0,1,2}] [-f] [-l] [--extractions-only]
                 [--extractions-locations EXTRACTIONS_LOCATIONS] [--plots-only]
                 [--plots-format PLOTS_FORMAT] [--primary PRIMARY] [--ymin YMIN] [--ymax YMAX]
                 [--vmin VMIN] [--vmax VMAX] [--cmap CMAP] [--row-ranges] [--column-ranges]
                 [--protocol-location PROTOCOL_LOCATIONS] [--regions-location REGIONS_LOCATIONS]
                 [--log-level LOG_LEVEL] [--log-file LOG_FILE]
                 [paths ...] [placeholders ...]

positional arguments:
  paths                 Paths of the datasets to process, can contain placeholders, e.g. {model}
  placeholders          Values for the placeholders in the from placeholder=value1,value2,...

options:
  -h, --help            show this help message and exit
  --datasets-path DATASETS_PATH
                        Base path for the input datasets
  --extractions-path EXTRACTIONS_PATH
                        Base path for the created extractions
  --plots-path PLOTS_PATH
                        Base path for the created plots
  -e EXTRACTIONS, --extractions EXTRACTIONS
                        Run only specific extractions (comma seperated)
  -a PLOTS, --plots PLOTS
                        Create only specific plots (comma seperated)
  -r REGIONS, --regions REGIONS
                        Extract only specific regions (comma seperated)
  -p PERIODS, --periods PERIODS
                        Extract only specific periods (comma seperated, format: YYYY_YYYY)
  -g {0,1,2}, --grid {0,1,2}
                        Maximum dimensions of the plot grid [default: 2]
  -f, --force           Always run extractions
  -l, --load            Load NetCDF datasets completely in memory
  --extractions-only    Only create extractions
  --extractions-locations EXTRACTIONS_LOCATIONS
                        URL or file path to the locations of extractions to fetch
  --plots-only          Only create plots
  --plots-format PLOTS_FORMAT
                        File format for plots [default: svg].
  --primary PRIMARY     Treat these placeholders as primary and plot them in color [default: all]
  --ymin YMIN           Fixed minimal y value for plots.
  --ymax YMAX           Fixed maximum y value for plots.
  --vmin VMIN           Fixed minimal colormap value for maps.
  --vmax VMAX           Fixed maximum colormap value for maps.
  --cmap CMAP           Colormap to use for maps.
  --row-ranges          Compute seperate plot ranges for each row.
  --column-ranges       Compute seperate plot ranges for each column.
  --protocol-location PROTOCOL_LOCATIONS
                        URL or file path to the protocol
  --regions-location REGIONS_LOCATIONS
                        Use the provided files to create the regions.
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file
```

The only mandatory argument is the path to an ISIMIP dataset, relative to the `DATASETS_PATH`, e.g. `ISIMIP3b/OutputData/water_global/CWatM/gfdl-esm4/historical/cwatm_gfdl-esm4_w5e5_historical_histsoc_default_qtot_global_daily`.

It makes sense to set at least `DATASETS_PATH` (location the NetCDF input files), `EXTRACTIONS_PATH` (location of the csv extractions), and `PLOTS_PATH` (location of the plots) to different directories, either by command line options or by a config file (in `isimip.conf` in the same directory, `~/.isimip.conf`, or `/etc/isimip.conf`):

```
[isimip-qa]
datasets_path = ~/data/isimip/qa/datasets
extractions_path = ~/data/isimip/qa/extractions
plots_path = ~/data/isimip/qa/plots

log_level = INFO
```

All other command line options can be set in the config file as well.

Datasets can be parametrized by the sytax:

```
isimip-qc path/to/dataset_with_{placeholder}.nc palceholder=value1,value2,...
```

E.g.

```
ISIMIP3b/OutputData/water_global/{model}/gfdl-esm4/historical/{model}_gfdl-esm4_w5e5_historical_histsoc_default_qtot_global_daily model=CWatM,H08
```

would process

```
ISIMIP3b/OutputData/water_global/CWatM/gfdl-esm4/historical/cwatm_gfdl-esm4_w5e5_historical_histsoc_default_qtot_global_daily
ISIMIP3b/OutputData/water_global/H08/gfdl-esm4/historical/h08_gfdl-esm4_w5e5_historical_histsoc_default_qtot_global_daily
```

Multiple identifier/specifier combinations can be used to create a grid of combinations.


Scripts/Notebooks
-----------------

The different functions of the tool can also be used in Python scripts or Jupyter Notebooks. Before any functions are called, the global settings object needs to be initialized, e.g.:

```python
from isimip_qa.main import init_settings

settings = init_settings(
    protocol_path='ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/',
    datasets_path='~/data/isimip/qa/datasets',
    extractions_path='~/data/isimip/qa/extractions',
    plots_path='~/data/isimip/qa/plots'
)
```

Alternatively the location of a config file can be given:

```python
from isimip_qa.main import init_settings

settings = init_settings(
    config_file='path/to/config/file'
)
```

Examples on how to use the tool in a script are given in the [notebooks](notebooks) folder.
