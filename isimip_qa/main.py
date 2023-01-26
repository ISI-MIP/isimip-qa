import argparse
import logging

import xarray as xr

from .config import settings

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('path', help='Path of the dataset to process, can contain indentifier placeholders, e.g. {model}')
    parser.add_argument('specifiers', nargs='*',
                        help='Specifiers in the from identifier=specifier1,specifier2,...')

    parser.add_argument('--config-file', dest='config_file',
                        help='File path of the config file')

    parser.add_argument('--datasets-path', dest='datasets_path',
                        help='base path for the input datasets')
    parser.add_argument('--extractions-path', dest='extractions_path',
                        help='base path for the output extractions')
    parser.add_argument('--assessments-path', dest='assessments_path',
                        help='base path for the output assessments')

    parser.add_argument('-a', '--assessments', dest='assessments', default=None,
                        help='Run only specific assessments (comma seperated)')
    parser.add_argument('-r', '--regions', dest='regions', default=None,
                        help='extract only specific regions (comma seperated)')
    parser.add_argument('-g', type=int, dest='grid', default=2, choices=[0, 1, 2],
                        help='Maximum dimensions of the plot grid [default: 2]')
    parser.add_argument('-i', '--include', dest='include_file',
                        help='Path to a file containing a list of files to include')
    parser.add_argument('-e', '--exclude', dest='exclude_file',
                        help='Path to a file containing a list of files to exclude')
    parser.add_argument('--protocol-location', dest='protocol_locations',
                        default='https://protocol.isimip.org https://protocol2.isimip.org',
                        help='URL or file path to the protocol')
    parser.add_argument('--log-level', dest='log_level', default='WARN',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='log_file',
                        help='Path to the log file')

    settings.setup(parser)

    # run extractions if they are not all complete already
    if not all([extraction.is_complete for extraction in settings.EXTRACTIONS]):
        for dataset in settings.DATASETS:
            for file_path in dataset.files:
                logger.info(f'load {file_path}')
                ds = xr.load_dataset(file_path)

                for extraction in settings.EXTRACTIONS:
                    for region in settings.REGIONS:
                        if region.type in extraction.region_types:
                            extraction.extract(dataset, region, ds)

    # run assessments
    for assessment in settings.ASSESSMENTS:
        assessment.plot()
