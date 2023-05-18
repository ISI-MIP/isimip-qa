import argparse
import logging

from .config import settings

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('path', help='Path of the dataset to process, can contain placeholders for specifiers, e.g. {model}')
    parser.add_argument('placeholders', nargs='*',
                        help='Values for the placeholders in the from placeholder=value1,value2,...')

    parser.add_argument('--config-file', dest='config_file',
                        help='File path of the config file')

    parser.add_argument('--datasets-path', dest='datasets_path',
                        help='base path for the input datasets')
    parser.add_argument('--extractions-path', dest='extractions_path',
                        help='base path for the output extractions')
    parser.add_argument('--assessments-path', dest='assessments_path',
                        help='base path for the output assessments')

    parser.add_argument('-e', '--extractions', dest='extractions', default=None,
                        help='Run only specific extractions (comma seperated)')
    parser.add_argument('-a', '--assessments', dest='assessments', default=None,
                        help='Run only specific assessments (comma seperated)')
    parser.add_argument('-r', '--regions', dest='regions', default=None,
                        help='extract only specific regions (comma seperated)')
    parser.add_argument('-g', '--grid', type=int, dest='grid', default=2, choices=[0, 1, 2],
                        help='Maximum dimensions of the plot grid [default: 2]')
    parser.add_argument('-f', '--force', dest='force', action='store_true', default=False,
                        help='Always run extractions')
    parser.add_argument('-l', '--load', dest='load', action='store_true', default=False,
                        help='Load NetCDF datasets completely in memory')
    parser.add_argument('--extractions-only', dest='extractions_only', action='store_true', default=False,
                        help='Run only assessments')
    parser.add_argument('--assessments-only', dest='assessments_only', action='store_true', default=False,
                        help='Run only assessments')

    parser.add_argument('--ymin', type=float, dest='ymin', default=None,
                        help='Fixed minimal y value for plots.')
    parser.add_argument('--ymax', type=float, dest='ymax', default=None,
                        help='Fixed maximum y value for plots.')

    parser.add_argument('--times', dest='times', default=None,
                        help='Time steps to use for maps (comma seperated)')
    parser.add_argument('--vmin', type=float, dest='vmin', default=None,
                        help='Fixed minimal colormap value for maps.')
    parser.add_argument('--vmax', type=float, dest='vmax', default=None,
                        help='Fixed maximum colormap value for maps.')
    parser.add_argument('--cmap', dest='cmap', default='viridis',
                        help='Colormap to use for maps.')

    parser.add_argument('--protocol-location', dest='protocol_locations',
                        default='https://protocol.isimip.org https://protocol2.isimip.org',
                        help='URL or file path to the protocol')
    parser.add_argument('--log-level', dest='log_level', default='WARN',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='log_file',
                        help='Path to the log file')

    settings.setup(parser)

    # run the extractions
    if not settings.ASSESSMENTS_ONLY:
        for dataset in settings.DATASETS:
            # check if the extraction is already complete
            if settings.FORCE:
                is_complete = False
            else:
                is_complete = True
                for extraction in settings.EXTRACTIONS:
                    for region in settings.REGIONS:
                        if extraction.region_types is None \
                                    or region.type in extraction.region_types:
                            is_complete &= extraction.exists(dataset, region)

            if not is_complete:
                for file in dataset.files:
                    file.load()
                    for extraction in settings.EXTRACTIONS:
                        for region in settings.REGIONS:
                            if extraction.region_types is None \
                                    or region.type in extraction.region_types:
                                extraction.extract(dataset, region, file)
                    file.unload()

    # run the assessments
    if not settings.EXTRACTIONS_ONLY:
        for assessment in settings.ASSESSMENTS:
            for extraction in settings.EXTRACTIONS:
                if assessment.extractions is None \
                        or extraction.specifier in assessment.extractions:
                    for region in settings.REGIONS:
                        if extraction.region_types is None \
                                or region.type in extraction.region_types:
                            if assessment.region_types is None \
                                    or region.type in assessment.region_types:
                                assessment.plot(extraction, region)
