import logging

import matplotlib.pyplot as plt

from ..config import settings
from ..mixins import SVGPlotMixin, GridPlotMixin
from ..models import Assessment
from ..exceptions import ExtractionNotFound
from ..extractions.attrs import AttrsExtraction


logger = logging.getLogger(__name__)


class DailyAssessment(SVGPlotMixin, GridPlotMixin, Assessment):

    specifier = 'daily'
    extractions = ['count', 'mean']

    def plot(self, extraction, region):
        path = self.get_path(extraction, region)
        logger.info(f'create plot {path}')

        plots = []
        for index, dataset in enumerate(settings.DATASETS):
            try:
                df = extraction.read(dataset, region)
                var = df.columns[0]
                attrs = AttrsExtraction().read(dataset, region)
                plots.append((index, df, var, attrs, dataset.primary))
            except ExtractionNotFound:
                continue

        nrows, ncols = self.get_grid()
        fig, axs = self.get_subplots(nrows, ncols)

        for index, df, var, attrs, primary in plots:
            irow, icol = self.get_grid_indexes(index)
            label = self.get_label(index)

            ymin = self.get_ymin(var, plots)
            ymax = self.get_ymax(var, plots)

            ax = axs.item(irow, icol)

            if primary:
                ax.plot(df.index, df[var], label=label, zorder=10)
                if label:
                    ax.legend(loc='lower left')
            else:
                ax.plot(df.index, df[var], color='grey', zorder=0)

            ax.set_title(self.get_title(index))
            ax.set_xlabel('date')
            ax.set_ylabel(f'{var} [{attrs.get("units")}]')
            ax.set_ylim(ymin, ymax)
            ax.tick_params(bottom=True, labelbottom=True, left=True, labelleft=True)

        path.parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(path, bbox_inches='tight')
        plt.close()
