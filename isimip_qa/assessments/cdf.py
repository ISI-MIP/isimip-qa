import logging

import matplotlib.pyplot as plt

from ..extractions import AttrsExtraction
from ..mixins import GridPlotMixin
from ..models import Assessment

logger = logging.getLogger(__name__)


class CDFAssessment(GridPlotMixin, Assessment):

    specifier = 'cdf'
    extractions = ['histogram']

    def get_df(self, dataset):
        extraction = self.extraction_class(dataset, self.region, self.period)
        df = extraction.read().set_index('bin')
        return df.cumsum() / df.sum()

    def get_attrs(self, dataset):
        return AttrsExtraction(dataset, self.region, self.period).read()

    def plot(self):
        logger.info(f'plot {self.extraction_class.specifier} {self.specifier} {self.region.specifier}')

        subplots = self.get_subplots()

        nrows, ncols = self.get_grid()
        fig, axs = self.get_figure(nrows, ncols)

        for sp in subplots:
            ax = axs.item(sp.irow, sp.icol)

            ymin = self.get_ymin(sp, subplots)
            ymax = self.get_ymax(sp, subplots)

            if sp.primary:
                ax.step(sp.df.index, sp.df[sp.var], where='mid', color=sp.color,
                        linestyle=sp.linestyle, label=sp.label, zorder=10)
                if sp.label:
                    ax.legend(loc='lower left').set_zorder(20)
            else:
                ax.step(sp.df.index, sp.df[sp.var], where='mid', color='grey', zorder=0)

            ax.set_title(sp.title)
            ax.set_xlabel(sp.attrs.get('standard_name'))
            ax.set_ylabel('CDF')
            ax.set_ylim(ymin, ymax)
            ax.tick_params(bottom=True, labelbottom=True, left=True, labelleft=True)

        if subplots:
            self.save_figure(fig, self.get_path())

        plt.close()
