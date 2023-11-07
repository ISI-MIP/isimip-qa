import logging

from ..extractions import AttrsExtraction
from ..mixins import FigurePlotMixin, GridPlotMixin
from ..models import Plot

logger = logging.getLogger(__name__)


class DailyPlot(FigurePlotMixin, GridPlotMixin, Plot):

    specifier = 'daily'
    extractions = ['count', 'mean']

    def get_df(self, dataset):
        extraction = self.extraction_class(dataset, self.region, self.period)
        return extraction.read()

    def get_attrs(self, dataset):
        return AttrsExtraction(dataset, self.region, self.period).read()

    def create(self):
        logger.info(f'plot {self.region.specifier} {self.extraction_class.specifier} {self.specifier}')

        subplots = self.get_subplots()
        if subplots:
            nrows, ncols = self.get_grid()
            fig, axs = self.get_figure(nrows, ncols)

            for sp in subplots:
                ax = axs.item(sp.irow, sp.icol)

                ymin = self.get_ymin(sp, subplots)
                ymax = self.get_ymax(sp, subplots)

                if sp.primary:
                    ax.plot(sp.df.index, sp.df[sp.var], label=sp.label, zorder=10)
                    if sp.label:
                        ax.legend(loc='lower left').set_zorder(20)
                else:
                    ax.plot(sp.df.index, sp.df[sp.var], color='grey', zorder=0)

                ax.set_title(sp.title)
                ax.set_xlabel('date')
                ax.set_ylabel(f'{sp.var} [{sp.attrs.get("units")}]')
                ax.set_ylim(ymin, ymax)
                ax.tick_params(bottom=True, labelbottom=True, left=True, labelleft=True)

            if self.path:
                self.write(fig, sp.path)
            else:
                self.show()
        else:
            logger.info('nothing to plot')
