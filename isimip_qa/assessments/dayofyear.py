import logging

import matplotlib.pyplot as plt

from ..config import settings
from ..extractions import PointExtraction, MaskExtraction
from ..mixins import SVGPlotMixin, GridPlotMixin
from ..models import Assessment

logger = logging.getLogger(__name__)


class DayOfYearMeanAssessment(SVGPlotMixin, GridPlotMixin, Assessment):

    specifier = 'dayofyearmean'
    extraction_classes = [PointExtraction, MaskExtraction]

    def plot(self, region):
        extraction = self.get_extraction(region)
        svg_path = self.get_svg_path(settings.DATASETS[0], region, self.specifier)

        logger.info(f'create plot {svg_path}')

        nrows, ncols = self.get_grid()
        fig, axs = plt.subplots(nrows, ncols, squeeze=False, figsize=(6 * ncols, 6 * nrows))

        for i, dataset in enumerate(settings.DATASETS):
            irow, icol = self.get_grid_indexes(i)
            label = self.get_label(i)
            variable = dataset.specifiers['variable']

            df, attrs = extraction.read(dataset, region)
            df = df.groupby(lambda x: x.dayofyear).mean()

            ax = axs.item(irow, icol)
            ax.step(df.index, df[df.columns[0]], where='mid', label=label)

            ax.set_title(self.get_title(i))
            ax.set_xlabel('day of the year')
            ax.set_ylabel(f'{variable} [{attrs.get("units")}]')
            if label:
                ax.legend(loc='lower left')

        svg_path.parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(svg_path, bbox_inches='tight')
