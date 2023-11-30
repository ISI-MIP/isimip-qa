import logging

from ..extractions import AttrsExtraction
from ..mixins import FigurePlotMixin, GridPlotMixin
from ..models import Plot

logger = logging.getLogger(__name__)


class YearlyPlot(FigurePlotMixin, GridPlotMixin, Plot):

    specifier = 'yearly'
    extractions = ['mean']

    def get_df(self, dataset):
        extraction = self.extraction_class(dataset, self.region, self.period)
        df = extraction.read()
        df_std = df.groupby(lambda x: x.year).std()
        df_mean = df.groupby(lambda x: x.year).mean()
        df_mean.insert(0, 'std', df_std)
        return df_mean

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

                        ax.step(sp.df.index, sp.df[sp.var], where='mid', label=sp.label,
                                color=sp.color, linestyle=sp.linestyle, zorder=sp.zorder)
                        ax.fill_between(sp.df.index, sp.df[sp.var] - sp.df['std'], sp.df[sp.var] + sp.df['std'],
                                        step='mid', alpha=0.3)

                        if sp.label:
                            ax.legend(loc='best').set_zorder(20)

                        xlabel = 'date'
                        ylabel = fr'${sp.var}_{{yearly}}$ [{sp.attrs.get("units")}]'

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
