import logging

import matplotlib.pyplot as plt

from ..config import settings
from ..mixins import SVGPlotMixin, GridPlotMixin
from ..models import Assessment
from ..extractions.attrs import AttrsExtraction

logger = logging.getLogger(__name__)


class DailyAssessment(SVGPlotMixin, GridPlotMixin, Assessment):

    specifier = 'daily'
    extractions = ['count', 'mean']

    def plot(self, extraction, region):
        path = self.get_path(settings.DATASETS[0], region, extraction)

        logger.info(f'create plot {path}')

        nrows, ncols = self.get_grid()
        fig, axs = plt.subplots(nrows, ncols, squeeze=False, figsize=(6 * ncols, 6 * nrows))

        for i, dataset in enumerate(settings.DATASETS):
            irow, icol = self.get_grid_indexes(i)
            label = self.get_label(i)

            df = extraction.read(dataset, region)

            var = df.columns[0]
            attrs = AttrsExtraction().read(dataset, region)

            ax = axs.item(irow, icol)
            ax.plot(df.index, df[var], label=label)

            ax.set_title(self.get_title(i))
            ax.set_xlabel('date')
            ax.set_ylabel(f'{var} [{attrs.get("units")}]')
            if label:
                ax.legend(loc='lower left')

        path.parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(path, bbox_inches='tight')
