import logging

import matplotlib.pyplot as plt
import pandas as pd

from ..config import settings
from ..extractions.attrs import AttrsExtraction
from ..mixins import GridPlotMixin
from ..models import Assessment

logger = logging.getLogger(__name__)


class MapAssessment(GridPlotMixin, Assessment):

    specifier = 'map'
    extractions = ['meanmap', 'countmap']

    def get_df(self, extraction, dataset, region):
        return extraction.read(dataset, region)

    def get_attrs(self, extraction, dataset, region):
        return AttrsExtraction().read(dataset, region)

    def plot(self, extraction, region):
        logger.info(f'plot {extraction.specifier} {region.specifier}')

        subplots = self.get_subplots(extraction, region)

        # get the extension of the valid data for all datasets
        lonmin, lonmax, latmin, latmax, ratio = -180, 180, -90, 90, 3.0
        if region.specifier != 'global':
            for sp in subplots:
                lonmin = max(lonmin, sp.df.where(pd.notnull(sp.df[sp.df.columns[-1]]))['lon'].min())
                lonmax = min(lonmax, sp.df.where(pd.notnull(sp.df[sp.df.columns[-1]]))['lon'].max())
                latmin = max(latmin, sp.df.where(pd.notnull(sp.df[sp.df.columns[-1]]))['lat'].min())
                latmax = min(latmax, sp.df.where(pd.notnull(sp.df[sp.df.columns[-1]]))['lat'].max())
            ratio = max((lonmax - lonmin) / (latmax - latmin), 1.0)

        nfigs, nrows, ncols = self.get_grid(figs=True)

        for ifig in range(nfigs):
            fig_subplots = [sp for sp in subplots if sp.ifig == ifig]

            fig, axs = self.get_figure(nrows, ncols, ratio=ratio)
            plt.subplots_adjust(top=1.1)

            cbars = []
            for sp in fig_subplots:
                ax = axs.item(sp.irow, sp.icol)

                vmin = self.get_vmin(sp, subplots)
                vmax = self.get_vmax(sp, subplots)

                df_pivot = sp.df.pivot(index='lat', columns=['lon'], values=sp.var)
                df_pivot = df_pivot.reindex(index=df_pivot.index[::-1])

                # truncate the dataframe at the extensions
                df_pivot = df_pivot.truncate(before=latmin, after=latmax)
                df_pivot = df_pivot.truncate(before=lonmin, after=lonmax, axis=1)

                im = ax.imshow(df_pivot, interpolation='nearest', label=sp.label,
                               extent=[lonmin, lonmax, latmin, latmax],
                               vmin=vmin, vmax=vmax, cmap=settings.CMAP)

                ax.set_title(sp.full_title, fontsize=10)
                ax.set_xlabel('lon', fontsize=10)
                ax.set_ylabel('lat', fontsize=10)
                ax.tick_params(bottom=True, labelbottom=True, left=True, labelleft=True)

                if ax not in cbars:
                    cbar = plt.colorbar(im, ax=ax)
                    cbar.set_label(f'{sp.var} [{sp.attrs.get("units")}]')
                    cbar.set_ticks([vmin, vmax])
                    cbars.append(ax)

            if fig_subplots:
                path = self.get_path(extraction, region, ifig)
                self.save_figure(fig, path)

            plt.close()
