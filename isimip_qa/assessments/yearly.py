import logging

import matplotlib.pyplot as plt

from ..config import settings
from ..mixins import SVGPlotMixin, GridPlotMixin
from ..models import Assessment
from ..exceptions import ExtractionNotFound
from ..extractions.attrs import AttrsExtraction

logger = logging.getLogger(__name__)


class YearlyAssessment(SVGPlotMixin, GridPlotMixin, Assessment):

    specifier = 'yearly'
    extractions = ['mean']

    def plot(self, extraction, region):
        path = self.get_path(extraction, region)
        logger.info(f'create plot {path}')

        plots = []
        for index, dataset in enumerate(settings.DATASETS):
            try:
                df = extraction.read(dataset, region).groupby(lambda x: x.year).mean()
                var = df.columns[0]
                attrs = AttrsExtraction().read(dataset, region)
                plots.append((index, df, var, attrs))
            except ExtractionNotFound:
                continue

        nrows, ncols = self.get_grid()
        fig, axs = self.get_subplots(nrows, ncols)

        for index, df, var, attrs in plots:
            irow, icol = self.get_grid_indexes(index)
            label = self.get_label(index)

            ymin = self.get_ymin(var, plots)
            ymax = self.get_ymax(var, plots)

            ax = axs.item(irow, icol)
            ax.step(df.index, df[var], where='mid', label=label)

            ax.set_title(self.get_title(index))
            ax.set_xlabel('date')
            ax.set_ylabel(f'{var} [{attrs.get("units")}]')
            ax.set_ylim(ymin, ymax)
            ax.tick_params(bottom=True, labelbottom=True, left=True, labelleft=True)
            if label:
                ax.legend(loc='lower left')

        path.parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(path, bbox_inches='tight')
        plt.close()
