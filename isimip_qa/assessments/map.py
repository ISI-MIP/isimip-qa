import logging

import matplotlib.pyplot as plt
import pandas as pd

from ..config import settings
from ..exceptions import ExtractionNotFound
from ..extractions.attrs import AttrsExtraction
from ..mixins import GridPlotMixin, PNGPlotMixin
from ..models import Assessment

logger = logging.getLogger(__name__)


class MapAssessment(PNGPlotMixin, GridPlotMixin, Assessment):

    specifier = 'map'
    extractions = ['slice']

    def plot(self, extraction, region):
        path = self.get_path(extraction, region)
        logger.info(f'create plot {path}' if path else f'create plot {extraction.specifier} {region.specifier}')

        plots = []
        for index, dataset in enumerate(self.datasets):
            try:
                df = extraction.read(dataset, region)
                var = df.columns[-1]
                attrs = AttrsExtraction().read(dataset, region)
                plots.append((index, df, var, attrs))
            except ExtractionNotFound:
                continue

        # get the extension of the valid data for all datasets
        lonmin, lonmax, latmin, latmax, ratio = -180, 180, -90, 90, 3.0
        if region.specifier != 'global':
            for index, df, var, attrs in plots:
                lonmin = max(lonmin, df.where(pd.notnull(df[df.columns[-1]]))['lon'].min())
                lonmax = min(lonmax, df.where(pd.notnull(df[df.columns[-1]]))['lon'].max())
                latmin = max(latmin, df.where(pd.notnull(df[df.columns[-1]]))['lat'].min())
                latmax = min(latmax, df.where(pd.notnull(df[df.columns[-1]]))['lat'].max())
            ratio = max((lonmax - lonmin) / (latmax - latmin), 1.0)

        nrows, ncols = self.get_grid()
        ntimes = 1 if settings.TIMES is None else len(settings.TIMES)
        ncols = ncols * ntimes
        fig, axs = self.get_subplots(nrows, ncols, ratio=ratio)
        plt.subplots_adjust(top=1.1)

        cbars = []
        for index, df, var, attrs in plots:
            irow, icol = self.get_grid_indexes(index)
            label = self.get_label(index)

            times = settings.TIMES or [df.index[0].strftime('%Y-%m-%d')]

            vmin = self.get_vmin(var, plots)
            vmax = self.get_vmax(var, plots)

            for time_index, time in enumerate(times):
                df_pivot = df.loc[time].pivot(index='lat', columns=['lon'], values=var)
                df_pivot = df_pivot.reindex(index=df_pivot.index[::-1])

                # truncate the dataframe at the extensions
                df_pivot = df_pivot.truncate(before=latmin, after=latmax)
                df_pivot = df_pivot.truncate(before=lonmin, after=lonmax, axis=1)

                ax = axs.item(irow, icol * ntimes + time_index)

                im = ax.imshow(df_pivot, interpolation='nearest', label=label,
                               extent=[lonmin, lonmax, latmin, latmax],
                               vmin=vmin, vmax=vmax, cmap=settings.CMAP)

                title = self.get_title(index)
                ax.set_title(f'{title} {time}' if title else time, fontsize=10)
                ax.set_xlabel('lon', fontsize=10)
                ax.set_ylabel('lat', fontsize=10)
                ax.tick_params(bottom=True, labelbottom=True, left=True, labelleft=True)

                if ax not in cbars:
                    cbar = plt.colorbar(im, ax=ax)
                    cbar.set_label(f'{var} [{attrs.get("units")}]')
                    cbar.set_ticks([vmin, vmax])
                    cbars.append(ax)
        if path:
            path.parent.mkdir(exist_ok=True, parents=True)
            fig.savefig(path, bbox_inches='tight')
            plt.close()
