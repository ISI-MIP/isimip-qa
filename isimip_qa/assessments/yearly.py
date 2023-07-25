import logging

import matplotlib.pyplot as plt

from ..exceptions import ExtractionNotFound
from ..extractions.attrs import AttrsExtraction
from ..mixins import GridPlotMixin, SVGPlotMixin
from ..models import Assessment

logger = logging.getLogger(__name__)


class YearlyAssessment(SVGPlotMixin, GridPlotMixin, Assessment):

    specifier = 'yearly'
    extractions = ['mean']

    def plot(self, extraction, region):
        logger.info(f'plot {extraction.specifier} {region.specifier}')

        plots = []
        for index, dataset in enumerate(self.datasets):
            try:
                df = extraction.read(dataset, region).groupby(lambda x: x.year).mean()
                var = df.columns[-1]
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
                ax.step(df.index, df[var], where='mid', label=label, zorder=10)
                if label:
                    ax.legend(loc='lower left')
            else:
                ax.step(df.index, df[var], where='mid', color='grey', zorder=0)

            ax.set_title(self.get_title(index))
            ax.set_xlabel('date')
            ax.set_ylabel(f'{var} [{attrs.get("units")}]')
            ax.set_ylim(ymin, ymax)
            ax.tick_params(bottom=True, labelbottom=True, left=True, labelleft=True)

        path = self.get_path(extraction, region)
        if path:
            logger.info(f'save {path}')
            path.parent.mkdir(exist_ok=True, parents=True)
            fig.savefig(path, bbox_inches='tight')
            plt.close()
