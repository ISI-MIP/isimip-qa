import argparse
import logging

from .config import settings
from .models import Dataset

from .assessments import assessment_classes

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

    for dataset_path in settings.DATASET_PATHS:
        dataset = Dataset(dataset_path)
        for assessment_class in assessment_classes:
            assessment = assessment_class(dataset)
            assessment.plot()
