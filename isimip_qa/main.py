import argparse
import logging

from .config import settings
from .models import Dataset

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('dataset_path', help='Path of the dataset to process')

    parser.add_argument('--config-file', dest='config_file',
                        help='File path of the config file')

    parser.add_argument('--input-path', dest='input_path',
                        help='base path for the input files')
    parser.add_argument('--output-path', dest='output_path',
                        help='base path for the output files')

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
    dataset = Dataset(settings.DATASET_PATH, settings.PATTERN, settings.INPUT_PATH, settings.OUTPUT_PATH)

    for file_path in dataset.files:
        print(file_path)
