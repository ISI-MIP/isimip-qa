import logging

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

        nrows, ncols = self.get_grid()
        fig, axs = plt.subplots(nrows, ncols * 2, squeeze=False, figsize=(30 * ncols, 60 * nrows))

        for i, dataset in enumerate(settings.DATASETS):
            irow, icol = self.get_grid_indexes(i)
            label = self.get_label(i)

            df = extraction.read(dataset, region)
            var = df.columns[-1]
            attrs = AttrsExtraction().read(dataset, region)

            for time_index, time in enumerate(settings.TIMES):
                df_pivot = df.loc[time].pivot(index='lat', columns=['lon'], values=var)
                df_pivot = df_pivot.reindex(index=df_pivot.index[::-1])

                ax = axs.item(irow, icol * 2 - time_index)
                ax.imshow(df_pivot, interpolation='nearest', label=label)

                ax.set_title(self.get_title(i))
                ax.set_xlabel('lon')
                ax.set_ylabel('lat')

        path.parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(path, bbox_inches='tight')
