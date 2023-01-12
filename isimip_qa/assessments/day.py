import logging

import matplotlib.pyplot as plt
import pandas as pd

from ..constants import points
from ..extractions import PointExtraction
from ..mixins import SVGPlotMixin, GridPlotMixin
from ..models import Assessment

logger = logging.getLogger(__name__)


class DayAssessment(SVGPlotMixin, GridPlotMixin, Assessment):

    extraction_classes = [PointExtraction]

    def plot(self, datasets):
        for place, lat, lon in points:
            svg_path = self.get_path(datasets, place, 'dayly')

            logger.info(f'create plot {svg_path}')

            nrows, ncols = self.get_grid()
            fig, axs = plt.subplots(nrows, ncols, squeeze=False, figsize=(6 * ncols, 6 * nrows))

            for i, dataset in enumerate(datasets):
                irow, icol = self.get_grid_indexes(i)
                label = self.get_label(i)
                variable = dataset.specifiers['variable']

                csv_path = PointExtraction().get_path(dataset, place)
                df = pd.read_csv(csv_path, index_col='time', parse_dates=['time'], infer_datetime_format=True)

                ax = axs.item(irow, icol)
                ax.plot(df.index, df[variable], label=label)

                ax.set_title(self.get_title(i))
                ax.set_xlabel('year')
                ax.set_ylabel(f'{variable}')
                if label:
                    ax.legend(loc='lower left')

            svg_path.parent.mkdir(exist_ok=True, parents=True)
            fig.savefig(svg_path, bbox_inches='tight')
