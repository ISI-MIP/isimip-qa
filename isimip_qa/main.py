import argparse

from .config import settings

from isimip_utils.patterns import match_dataset_path


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('path', help='Path of the dataset to process')

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

    dataset_path, specifiers = match_dataset_path(settings.PATTERN, settings.PATH)

    for file_name in settings.PATH.parent.glob(f'{settings.PATH.stem}*'):
        print(file_name)
