import logging

import pandas as pd
import matplotlib.pyplot as plt

from ..config import settings
from ..mixins import PNGPlotMixin, GridPlotMixin
from ..models import Assessment
from ..extractions.attrs import AttrsExtraction

logger = logging.getLogger(__name__)


class MapAssessment(PNGPlotMixin, GridPlotMixin, Assessment):

    specifier = 'map'
    extractions = ['map']

    def plot(self, extraction, region):
        path = self.get_path(settings.DATASETS[0], region, extraction)

        logger.info(f'create plot {path}')

        # read all dataframes to determine min/max values
        dfs = []
        for dataset in settings.DATASETS:
            dfs.append(extraction.read(dataset, region))

        # get the extension of the valid data for all datasets
        if region.specifier == 'global':
            lonmin, lonmax, latmin, latmax = -180, 180, -90, 90
            ratio = 3
        else:
            lonmin = min([df.where(pd.notnull(df[df.columns[-1]]))['lon'].min() for df in dfs])
            lonmax = max([df.where(pd.notnull(df[df.columns[-1]]))['lon'].max() for df in dfs])
            latmin = min([df.where(pd.notnull(df[df.columns[-1]]))['lat'].min() for df in dfs])
            latmax = max([df.where(pd.notnull(df[df.columns[-1]]))['lat'].max() for df in dfs])
            ratio = max((lonmax - lonmin) / (latmax - latmin), 1.0)

        nrows, ncols = self.get_grid()
        ntimes = 1 if settings.TIMES is None else len(settings.TIMES)
        ncols = ncols * ntimes
        fig, axs = plt.subplots(nrows, ncols, squeeze=False, figsize=(4 * ratio * ncols, 4 * nrows))
        plt.subplots_adjust(top=1.1)

        # get the min/max for the colorbar in "variable" space
        vmin = min([df[df.columns[-1]].min() for df in dfs]) if settings.VMIN is None else settings.VMIN
        vmax = max([df[df.columns[-1]].max() for df in dfs]) if settings.VMAX is None else settings.VMAX

        for i, dataset in enumerate(settings.DATASETS):
            irow, icol = self.get_grid_indexes(i)
            label = self.get_label(i)

            df = dfs[i]
            var = df.columns[-1]
            attrs = AttrsExtraction().read(dataset, region)
            times = settings.TIMES or [df.index[0].strftime('%Y-%m-%d')]

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

                title = self.get_title(i)
                ax.set_title(f'{title} {time}' if title else time, fontsize=10)
                ax.set_xlabel('lon', fontsize=10)
                ax.set_ylabel('lat', fontsize=10)

                cbar = plt.colorbar(im, ax=ax)
                cbar.set_label(f'{var} [{attrs.get("units")}]')
                if (settings.VMIN and settings.VMAX):
                    cbar.set_ticks([vmin, (vmax-vmin) * 0.5, vmax])

        path.parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(path, bbox_inches='tight')
