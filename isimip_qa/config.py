import re
from collections import defaultdict
from itertools import product
from pathlib import Path

import xarray as xr

from isimip_utils.config import Settings as BaseSettings
from isimip_utils.decorators import cached_property
from isimip_utils.fetch import fetch_json


class Settings(BaseSettings):

    def setup(self, args):
        super().setup(args)

        # create a dict to store masks
        self.MASKS = {}

    @cached_property
    def PATHS(self):
        paths = self.args.get('PATHS')
        if paths:
            return [Path(path).expanduser() for path in paths]

    @cached_property
    def PLACEHOLDERS(self):
        placeholders_dict = defaultdict(list)
        placeholders_strings = self.args.get('PLACEHOLDERS')
        if placeholders_strings:
            for placeholders_string in placeholders_strings:
                placeholder, values = placeholders_string.split('=')
                placeholders_dict[placeholder] += values.split(',')
        return placeholders_dict

    @cached_property
    def DATASETS(self):
        if self.PATHS is None:
            RuntimeError('You need to provide at least one path.')

        if self.PLACEHOLDERS:
            datasets = []
            placeholder_permutations = list(product(*self.PLACEHOLDERS.values()))

            for input_path in self.PATHS:
                for permutations in placeholder_permutations:
                    placeholders = dict(zip(self.PLACEHOLDERS.keys(), permutations))

                    try:
                        path_str = str(input_path).format(**placeholders)
                    except KeyError as e:
                        raise RuntimeError('Some of the placeholders are missing.') from e

                    path = Path(path_str)
                    path = path.parent / path.name.lower()  # ensure that the name of the path is lower case
                    datasets.append(path)

            return datasets
        else:
            for input_path in self.PATHS:
                if re.search(r'\{.*\}', str(input_path)):
                    raise RuntimeError('Some of the placeholders are missing.')

            return self.PATHS

    @cached_property
    def DATASETS_PATH(self):
        return Path(self.args['DATASETS_PATH']).expanduser() if self.args['DATASETS_PATH'] else Path.cwd()

    @cached_property
    def EXTRACTIONS_PATH(self):
        return Path(self.args['EXTRACTIONS_PATH']).expanduser() if self.args['EXTRACTIONS_PATH'] else Path.cwd()

    @cached_property
    def PLOTS_PATH(self):
        return Path(self.args['PLOTS_PATH']).expanduser() if self.args['PLOTS_PATH'] else Path.cwd()

    @cached_property
    def REGIONS(self):
        regions_strings = self.args.get('REGIONS')
        if regions_strings:
            regions = []
            for regions_string in regions_strings.split(','):
                regions += list(filter(lambda r: r.get('specifier', '').startswith(regions_string), self.REGIONS_LIST))
            return regions
        else:
            # return only the global region
            return [{'type': 'global', 'specifier': 'global'}]

    @cached_property
    def REGIONS_LIST(self):
        regions_list = [{'type': 'global', 'specifier': 'global'}]

        for file in Path(__file__).parent.joinpath('regions').iterdir():
            default_regions = fetch_json([str(file)])
            if default_regions is not None:
                regions_list += default_regions

        if self.REGIONS_LOCATIONS:
            input_regions = fetch_json(self.REGIONS_LOCATIONS)
            if input_regions is not None:
                regions_list += input_regions

        return regions_list

    @cached_property
    def PERIODS(self):
        periods_strings = self.args.get('PERIODS')
        if periods_strings:
            periods = []
            for period_string in periods_strings.split(','):
                start_date, end_date = period_string.split('-')
                periods.append({'type': 'slice', 'start_date': start_date, 'end_date': end_date})
            return periods
        else:
            return [{'type': 'auto'}]

    @cached_property
    def EXTRACTIONS(self):
        return self.args.get('EXTRACTIONS').split(',')

    @cached_property
    def PLOTS(self):
        return self.args.get('PLOTS').split(',')

    @cached_property
    def PRIMARY(self):
        return self.args.get('PRIMARY').split(',') if self.args.get('PRIMARY') else []

    @cached_property
    def GRIDAREA(self):
        if self.args.get('GRIDAREA'):
            ds = xr.load_dataset(self.args.get('GRIDAREA'))
            ds = ds.isel(lon=0)
            return ds.cell_area

    @cached_property
    def REGIONS_LOCATIONS(self):
        return self.args.get('REGIONS_LOCATIONS').split()

    @cached_property
    def EXTRACTIONS_LOCATIONS(self):
        return self.args.get('EXTRACTIONS_LOCATIONS').split()


settings = Settings()
