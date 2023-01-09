import logging

import matplotlib.pyplot as plt
import pandas as pd

from ..config import settings
from ..constants import points
from ..extractions import PointExtraction
from ..models import Assessment

logger = logging.getLogger(__name__)


class YearlyAssessment(Assessment):

    extraction_classes = [PointExtraction]

    def plot(self, datasets):
        for place, lat, lon in points:
            svg_path = self.get_path(datasets[0], place)

            logger.info(f'create plot {svg_path}')
            fig = plt.figure(figsize=(20, 10))

            for dataset in datasets:
                variable = dataset.specifiers['variable']
                csv_path = PointExtraction().get_path(dataset, place)
                df = pd.read_csv(csv_path, index_col='time', parse_dates=['time'], infer_datetime_format=True) \
                       .groupby(lambda x: x.year).mean()
                plt.plot(df.index, df[variable], label=dataset.path.name)

            plt.title(svg_path.name)
            plt.xlabel('year')
            plt.ylabel(f'mean {variable}')
            plt.legend(loc='lower left')

            svg_path.parent.mkdir(exist_ok=True, parents=True)
            fig.savefig(svg_path, bbox_inches='tight')

    def get_path(self, dataset, place):
        path = dataset.replace_name(region=place, time_step='yearly', **settings.SPECIFIERS)
        return settings.ASSESSMENTS_PATH.joinpath(path.name).with_suffix('.svg')
