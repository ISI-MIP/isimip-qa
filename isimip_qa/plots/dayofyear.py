import logging

from ..extractions import AttrsExtraction
from ..mixins import FigurePlotMixin, GridPlotMixin
from ..models import Plot

logger = logging.getLogger(__name__)


class DayOfYearPlot(FigurePlotMixin, GridPlotMixin, Plot):

    specifier = 'dayofyear'
    extractions = ['mean']

    def get_df(self, dataset):
        extraction = self.extraction_class(dataset, self.region, self.period)
        return extraction.read().groupby(lambda x: x.dayofyear).mean()

    def get_attrs(self, dataset):
        return AttrsExtraction(dataset, self.region, self.period).read()

    def create(self):
        logger.info(f'plot {self.region.specifier} {self.extraction_class.specifier} {self.specifier}')

        nfigs, nrows, ncols = self.get_grid()
        subplots = self.get_subplots()
        if subplots:
            for ifig in range(nfigs):
                fig_path = self.get_figure_path(ifig)
                fig_subplots = [sp for sp in subplots if sp.ifig == ifig]

                if fig_subplots:
                    fig, axs = self.get_figure(nrows, ncols)

                    for sp in fig_subplots:
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
                        ax.set_xlabel('day of the year')
                        ax.set_ylabel(f'{sp.var} [{sp.attrs.get("units")}]')
                        ax.set_ylim(ymin, ymax)
                        ax.tick_params(bottom=True, labelbottom=True, left=True, labelleft=True)

                    if fig_path:
                        self.write(fig, fig_path)
                    else:
                        self.show()
        else:
            logger.info('nothing to plot')
