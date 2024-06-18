import logging

from ..extractions import AttrsExtraction
from ..mixins import FigurePlotMixin, GridPlotMixin
from ..models import Plot

logger = logging.getLogger(__name__)


class DailyPlot(FigurePlotMixin, GridPlotMixin, Plot):

    specifier = 'daily'
    extractions = ['count']

    def get_df(self, dataset):
        extraction = self.extraction_class(dataset, self.region, self.period)
        ds = extraction.read()
        df = ds.to_dataframe()
        df.attrs = {varname: var.attrs for varname, var in ds.variables.items()}

        return df

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

                        ax.plot(sp.df.index, sp.df[sp.var], label=sp.label,
                                color=sp.color, linestyle=sp.linestyle, zorder=sp.zorder)

                        if sp.label:
                            ax.legend(loc='best').set_zorder(20)

                        xlabel = 'date'
                        if self.extraction_class.specifier == 'count':
                            ylabel = f'{sp.var} [count]'
                        else:
                            ylabel = f'{sp.var} [{sp.attrs.get("units")}]'

                        ax.set_title(sp.title)
                        ax.set_xlabel(xlabel)
                        ax.set_ylabel(ylabel)
                        ax.set_ylim(ymin, ymax)
                        ax.tick_params(bottom=True, labelbottom=True, left=True, labelleft=True)

                    if fig_path:
                        self.write(fig, fig_path)
                    else:
                        self.show()
        else:
            logger.info('nothing to plot')
