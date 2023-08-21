import logging

import matplotlib.pyplot as plt

from ..extractions.attrs import AttrsExtraction
from ..mixins import GridPlotMixin
from ..models import Assessment

logger = logging.getLogger(__name__)


class MonthOfYearAssessment(GridPlotMixin, Assessment):

    specifier = 'monthofyear'
    extractions = ['mean']

    def get_df(self, extraction, dataset, region):
        return extraction.read(dataset, region).groupby(lambda x: x.month).mean()

    def get_attrs(self, extraction, dataset, region):
        return AttrsExtraction().read(dataset, region)

    def plot(self, extraction, region):
        logger.info(f'plot {extraction.specifier} {region.specifier}')

        subplots = self.get_subplots(extraction, region)

        nrows, ncols = self.get_grid()
        fig, axs = self.get_figure(nrows, ncols)

        for sp in subplots:
            ax = axs.item(sp.irow, sp.icol)

            ymin = self.get_ymin(sp, subplots)
            ymax = self.get_ymax(sp, subplots)

            if sp.primary:
                ax.step(sp.df.index, sp.df[sp.var], where='mid', color=sp.color, linestyle=sp.linestyle, label=sp.label, zorder=10)
                if sp.label:
                    ax.legend(loc='lower left').set_zorder(20)
            else:
                ax.step(sp.df.index, sp.df[sp.var], where='mid', color='grey', zorder=0)

            ax.set_title(sp.title)
            ax.set_xlabel('month of the year')
            ax.set_ylabel(f'{sp.var} [{sp.attrs.get("units")}]')
            ax.set_ylim(ymin, ymax)
            ax.tick_params(bottom=True, labelbottom=True, left=True, labelleft=True)

        path = self.get_path(extraction, region)
        if path:
            path = path.with_suffix('.svg')
            logger.info(f'save {path}')
            path.parent.mkdir(exist_ok=True, parents=True)
            fig.savefig(path, bbox_inches='tight')
            plt.close()
