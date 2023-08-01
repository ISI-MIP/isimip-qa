import logging

import matplotlib.pyplot as plt

from ..extractions.attrs import AttrsExtraction
from ..mixins import GridPlotMixin, SVGPlotMixin
from ..models import Assessment

logger = logging.getLogger(__name__)


class DayOfYearAssessment(SVGPlotMixin, GridPlotMixin, Assessment):

    specifier = 'dayofyear'
    extractions = ['mean']

    def get_df(self, extraction, dataset, region):
        return extraction.read(dataset, region).groupby(lambda x: x.dayofyear).mean()

    def get_attrs(self, extraction, dataset, region):
        return AttrsExtraction().read(dataset, region)

    def plot(self, extraction, region):
        logger.info(f'plot {extraction.specifier} {region.specifier}')

        subplots = self.get_subplots(extraction, region)

        nrows, ncols = self.get_grid()
        fig, axs = self.get_figure(nrows, ncols)

        for sp in subplots:
            ax = axs.item(sp.irow, sp.icol)

            ymin = self.get_ymin(sp.irow, sp.icol, subplots)
            ymax = self.get_ymax(sp.irow, sp.icol, subplots)

            if sp.primary:
                ax.scatter(sp.df.index, sp.df[sp.var], s=10, marker='.', label=sp.label, zorder=10)
                if sp.label:
                    ax.legend(loc='lower left').set_zorder(20)
            else:
                ax.scatter(sp.df.index, sp.df[sp.var], s=10, marker='.', color='grey', zorder=0)

            ax.set_title(sp.title)
            ax.set_xlabel('day of the year')
            ax.set_ylabel(f'{sp.var} [{sp.attrs.get("units")}]')
            ax.set_ylim(ymin, ymax)
            ax.tick_params(bottom=True, labelbottom=True, left=True, labelleft=True)

        path = self.get_path(extraction, region)
        if path:
            logger.info(f'save {path}')
            path.parent.mkdir(exist_ok=True, parents=True)
            fig.savefig(path, bbox_inches='tight')
            plt.close()
