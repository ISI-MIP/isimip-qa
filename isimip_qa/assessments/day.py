import logging

import matplotlib.pyplot as plt
import pandas as pd

from ..config import settings
from ..extractions import PointExtraction, MaskExtraction
from ..mixins import SVGPlotMixin, GridPlotMixin
from ..models import Assessment

logger = logging.getLogger(__name__)


class DayAssessment(SVGPlotMixin, GridPlotMixin, Assessment):

    specifier = 'daily'
    extraction_classes = [PointExtraction, MaskExtraction]

    def plot(self):
        for region in settings.REGIONS:
            svg_path = self.get_path(settings.DATASETS[0], region, self.specifier)

            logger.info(f'create plot {svg_path}')

            nrows, ncols = self.get_grid()
            fig, axs = plt.subplots(nrows, ncols, squeeze=False, figsize=(6 * ncols, 6 * nrows))

            for i, dataset in enumerate(settings.DATASETS):
                irow, icol = self.get_grid_indexes(i)
                label = self.get_label(i)
                variable = dataset.specifiers['variable']

                if region.type == 'point':
                    csv_path = PointExtraction().get_path(dataset, region)
                elif region.type == 'mask':
                    csv_path = MaskExtraction().get_path(dataset, region)

                df = pd.read_csv(csv_path, index_col='time', parse_dates=['time'], infer_datetime_format=True)

                ax = axs.item(irow, icol)
                ax.plot(df.index, df[variable], label=label)

                ax.set_title(self.get_title(i))
                ax.set_xlabel('date')
                ax.set_ylabel(f'{variable}')
                if label:
                    ax.legend(loc='lower left')

            svg_path.parent.mkdir(exist_ok=True, parents=True)
            fig.savefig(svg_path, bbox_inches='tight')
