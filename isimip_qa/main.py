import logging

from isimip_utils.parser import ArgumentParser

from .config import settings
from .extractions import extraction_classes
from .models import Dataset, Period, Region
from .parser import ArgumentAction
from .plots import plot_classes

logger = logging.getLogger(__name__)


def get_parser():
    parser = ArgumentParser(prog='isimip-qa')

    parser.add_argument('paths', nargs='*', action=ArgumentAction,
                        help='Paths of the datasets to process, can contain placeholders, e.g. {model}')
    parser.add_argument('placeholders', nargs='*', action=ArgumentAction,
                        help='Values for the placeholders in the from placeholder=value1,value2,...')

    parser.add_argument('--datasets-path', dest='datasets_path',
                        help='Base path for the input datasets')
    parser.add_argument('--extractions-path', dest='extractions_path',
                        help='Base path for the created extractions')
    parser.add_argument('--plots-path', dest='plots_path',
                        help='Base path for the created plots')

    parser.add_argument('--extractions', dest='extractions', default=None,
                        help='Run only specific extractions (comma seperated)')
    parser.add_argument('--plots', dest='plots', default=None,
                        help='Create only specific plots (comma seperated)')
    parser.add_argument('-r', '--regions', dest='regions', default='global',
                        help='Extract only specific regions (comma seperated)')
    parser.add_argument('-p', '--periods', dest='periods', default=None,
                        help='Extract only specific periods (comma seperated, format: YYYY_YYYY)')

    parser.add_argument('-g', '--grid', type=int, dest='grid', default=0, choices=[0, 1, 2],
                        help='Number of dimensions of the plot grid [default: 0, i.e. one plot]')
    parser.add_argument('-f', '--force', dest='force', action='store_true', default=False,
                        help='Always run extractions')
    parser.add_argument('-l', '--load', dest='load', action='store_true', default=False,
                        help='Load NetCDF datasets completely in memory')

    parser.add_argument('--extractions-only', dest='extractions_only', action='store_true', default=False,
                        help='Only create extractions')
    parser.add_argument('--extractions-locations', dest='extractions_locations',
                        default='https://files.isimip.org/qa/extractions/',
                        help='URL or file path to the locations of extractions to fetch')
    parser.add_argument('--plots-only', dest='plots_only', action='store_true', default=False,
                        help='Only create plots')
    parser.add_argument('--plots-format', dest='plots_format', default='svg',
                        help='File format for plots [default: svg].')
    parser.add_argument('--primary', dest='primary', default=None,
                        help='Treat these placeholders as primary and plot them in color [default: all]')

    parser.add_argument('--ymin', type=float, dest='ymin', default=None,
                        help='Fixed minimal y value for plots.')
    parser.add_argument('--ymax', type=float, dest='ymax', default=None,
                        help='Fixed maximum y value for plots.')

    parser.add_argument('--vmin', type=float, dest='vmin', default=None,
                        help='Fixed minimal colormap value for maps.')
    parser.add_argument('--vmax', type=float, dest='vmax', default=None,
                        help='Fixed maximum colormap value for maps.')
    parser.add_argument('--cmap', dest='cmap', default='viridis',
                        help='Colormap to use for maps.')

    parser.add_argument('--row-ranges', dest='row_ranges', action='store_true', default=False,
                        help='Compute seperate plot ranges for each row.')
    parser.add_argument('--column-ranges', dest='column_ranges', action='store_true', default=False,
                        help='Compute seperate plot ranges for each column.')

    parser.add_argument('--protocol-location', dest='protocol_locations',
                        default='https://protocol.isimip.org https://protocol2.isimip.org',
                        help='URL or file path to the protocol')
    parser.add_argument('--regions-location', dest='regions_locations', default='',
                        help='Use the provided files to create the regions.')
    parser.add_argument('--log-level', dest='log_level', default='WARN',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='log_file',
                        help='Path to the log file')

    return parser


def init_settings(config_file=None, **kwargs):
    parser = get_parser()
    parser.config_file = config_file
    args = parser.get_defaults()
    args.update(kwargs)
    settings.setup(args)
    return settings


def main():
    parser = get_parser()
    args = vars(parser.parse_args())
    settings.setup(args)

    # create list of datasets
    datasets = [Dataset(path) for path in settings.DATASETS]

    # create list of regions and periods
    regions = [Region(**region) for region in settings.REGIONS]
    periods = [Period(**period) for period in settings.PERIODS]

    # run the extractions
    if not settings.PLOTS_ONLY:
        for dataset in datasets:
            extractions = []
            for region in regions:
                for period in periods:
                    for extraction_class in extraction_classes:
                        if (
                            (settings.EXTRACTIONS is None or extraction_class.specifier in settings.EXTRACTIONS)
                            and extraction_class.has_region(region)
                            and extraction_class.has_period(period)
                        ):
                            extraction = extraction_class(dataset, region, period)
                            if settings.FORCE or (not extraction.exists() and not extraction.fetch()):
                                extractions.append(extraction)

            if extractions:
                # if at least one extraction is not complete, perform extractions file by file
                for file in dataset.files:
                    file.open()
                    for extraction in extractions:
                        extraction.extract(file)
                    file.close()

    # create the plots
    if not settings.EXTRACTIONS_ONLY:
        for plot_class in plot_classes:
            for region in regions:
                for period in periods:
                    for extraction_class in extraction_classes:
                        if (
                            (settings.EXTRACTIONS is None or extraction_class.specifier in settings.EXTRACTIONS)
                            and extraction_class.has_region(region)
                            and extraction_class.has_period(period)
                        ):
                            if (
                                (settings.PLOTS is None or plot_class.specifier in settings.PLOTS)
                                and plot_class.has_extraction(extraction_class)
                                and extraction_class.has_region(region)
                                and extraction_class.has_period(period)
                            ):
                                plot = plot_class(extraction_class, datasets, region, period, save=True,
                                                  dimensions=settings.PLACEHOLDERS, grid=settings.GRID)
                                plot.create()
