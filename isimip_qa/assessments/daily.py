import logging

import matplotlib.pyplot as plt
import pandas as pd

from ..config import settings
from ..constants import points
from ..extractions import PointExtraction
from ..models import Assessment

logger = logging.getLogger(__name__)


class DayAssessment(Assessment):

    def plot(self):
        variable = self.dataset.specifiers['variable']

        extraction = PointExtraction(self.dataset, points)
        if not extraction.is_complete:
            extraction.run()

        for place, lat, lon in points:
            csv_path = extraction.get_csv_path(place)
            svg_path = self.get_svg_path(place)
            if not svg_path.exists():
                logger.info(f'create plot {svg_path}')

                df = pd.read_csv(csv_path, index_col='time', parse_dates=['time'], infer_datetime_format=True)

                fig = plt.figure(figsize=(20, 10))
                plt.plot(df.index, df[variable])
                plt.title(svg_path.name)
                plt.xlabel('day')
                plt.ylabel(f'mean {variable}')

                svg_path.parent.mkdir(exist_ok=True, parents=True)
                fig.savefig(svg_path, bbox_inches='tight')

    def get_svg_path(self, place):
        region = self.dataset.specifiers['region']
        path_str = str(self.dataset.path).replace(f'_{region}_', f'_{place}_')
        return settings.ASSESSMENTS_PATH.joinpath(path_str).with_suffix('.svg')
