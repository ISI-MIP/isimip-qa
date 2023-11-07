import logging
from itertools import chain, product
from pathlib import Path

import matplotlib.pyplot as plt

from ..config import settings
from ..exceptions import ExtractionNotFound
from ..models import Subplot

logger = logging.getLogger(__name__)


class FigurePlotMixin:

    def write(self, fig, path):
        path.parent.mkdir(exist_ok=True, parents=True)

        logger.info(f'write {path}')
        try:
            fig.savefig(path, bbox_inches='tight')
        except ValueError as e:
            logger.error(f'could not save {path} ({e})')
        plt.close()

    def show(self):
        plt.show()
        plt.close()


class GridPlotMixin:

    colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c',
        '#d62728', '#9467bd', '#8c564b',
        '#e377c2', '#bcbd22', '#17becf'
    ]
    linestyles = ['solid', 'dashed', 'dashdot', 'dotted']
    markers = ['.', '*', 'D', 's']

    def __init__(self, *args, path=None, dimensions=None, grid=2, **kwargs):
        self.path = Path(path)
        self.dimensions = dimensions
        self.grid = grid
        if self.dimensions:
            self.keys = list(self.dimensions.keys())
            self.values = list(self.dimensions.values())
            self.permutations = list(product(*self.values))
            self.styles = self.get_styles()
        super().__init__(*args, **kwargs)

    def get_figure(self, nrows, ncols, ratio=1):
        fig, axs = plt.subplots(nrows, ncols, squeeze=False, figsize=(6 * ratio * ncols, 6 * nrows))
        for ax in chain.from_iterable(axs):
            ax.tick_params(bottom=False, labelbottom=False, left=False, labelleft=False)
        return fig, axs

    def get_path(self, ifig):
        if not self.path.suffix:
            self.path = self.path.with_suffix('.' + settings.PLOTS_FORMAT)

        stem = self.path.stem

        if self.dimensions:
            placeholders = {}

            for j, key in enumerate(self.keys):
                if ifig is None or j < self.grid:
                    primary_values = [value for value in self.values[j] if value in settings.PRIMARY]
                    if primary_values:
                        values_strings = primary_values
                    elif len(self.values[j]) < 10:
                        values_strings = self.values[j]
                    else:
                        values_strings = ['various']
                else:
                    # this works because for j > self.grid, the permutations
                    # only repeat with a "period" of nfig
                    values_strings = [self.permutations[ifig][j]]

                placeholders[key] = '+'.join(values_strings).lower()

            # apply placeholders
            stem = stem.format(**placeholders)

        # overwrite _global_ with the region, this is not very elegant,
        # but after a lot (!) of experiments, this is the best solution ...
        if '_global_' in stem:
            stem = stem.replace('_global_', '_' + self.region.specifier + '_')
        else:
            stem += '_global'

        # add the extration and the plot specifiers
        stem = f'{stem}_{self.extraction_class.specifier}_{self.specifier}'

        if self.period.type == 'slice':
            stem = f'{stem}_{self.period.start_date}_{self.period.end_date}'

        return settings.PLOTS_PATH / self.path.with_stem(stem)

    def get_grid(self, figs=False):
        grid = [1, 1, 1] if figs else [1, 1]

        if self.dimensions:
            for j, key in enumerate(self.keys):
                ndim = len(self.dimensions[key])

                if j < self.grid:
                    grid[j] = ndim

                if figs:
                    if j == self.grid:
                        grid[-1] = len(self.values[j])
                    elif j > self.grid:
                        grid[-1] *= len(self.values[j])

        return reversed(grid)

    def get_grid_indexes(self, i):
        grid_indexes = [0, 0, 0]

        if self.dimensions:
            permutation = self.permutations[i]

            for j, key in enumerate(self.keys):
                value = permutation[j]
                value_index = self.dimensions[key].index(value)

                if j < self.grid:
                    grid_indexes[j] = value_index
                elif j == len(self.keys) - 1:
                    grid_indexes[-1] += value_index
                else:
                    grid_indexes[-1] += value_index * len(self.values[j+1])

        return reversed(grid_indexes)

    def get_styles(self):
        # create a specific style for each label
        styles = {}
        for permutation in self.permutations:
            label = permutation[self.grid:]
            if label not in styles:
                index = len(styles.keys())
                color_index = index % len(self.colors)
                linestyle_index = int(index / len(self.colors)) % len(self.linestyles)
                marker_index = int(index / len(self.colors)) % len(self.markers)
                styles[label] = (
                    self.colors[color_index],
                    self.linestyles[linestyle_index],
                    self.markers[marker_index]
                )
        return styles

    def get_primary(self, i):
        if self.dimensions and settings.PRIMARY:
            permutation = self.permutations[i]

            for j, key in enumerate(self.keys):
                if permutation[j] in settings.PRIMARY:
                    return True

            return False
        else:
            return True

    def get_subplots(self):
        subplots = []
        for dataset_index, dataset in enumerate(self.datasets):
            # adjust the index when using multiple PATHS as input
            if self.dimensions:
                index = dataset_index % len(self.permutations)
            else:
                index = dataset_index

            ifig, irow, icol = self.get_grid_indexes(index)

            try:
                df = self.get_df(dataset)
            except ExtractionNotFound:
                continue

            try:

                attrs = self.get_attrs(dataset)
            except ExtractionNotFound:
                attrs = {}

            var = df.columns[-1]

            subplot = Subplot(
                df=df,
                attrs=attrs,
                var=var,
                label=self.get_label(index),
                title=self.get_title(index),
                full_title=self.get_full_title(index),
                color=self.get_color(index),
                linestyle=self.get_linestyle(index),
                marker=self.get_marker(index),
                ifig=ifig,
                irow=irow,
                icol=icol,
                primary=self.get_primary(index),
                path=self.get_path(ifig)
            )

            subplots.append(subplot)

        return subplots

    def get_df(self, dataset):
        raise NotImplementedError

    def get_attrs(self, dataset):
        raise NotImplementedError

    def get_full_title(self, i):
        if self.dimensions:
            return ' '.join(self.permutations[i])

    def get_title(self, i):
        if self.dimensions:
            return ' '.join(self.permutations[i][:self.grid])

    def get_label(self, i):
        if self.dimensions:
            return ' '.join(self.permutations[i][self.grid:])

    def get_color(self, i):
        if self.dimensions:
            return self.styles[self.permutations[i][self.grid:]][0]

    def get_linestyle(self, i):
        if self.dimensions:
            return self.styles[self.permutations[i][self.grid:]][1]

    def get_marker(self, i):
        if self.dimensions:
            return self.styles[self.permutations[i][self.grid:]][2]

    def get_ymin(self, subplot, subplots):
        if settings.YMIN is None:
            return min([sp.df[sp.var].min() for sp in subplots
                        if self.is_in_same_plot(sp, subplot)]) * 0.99
        else:
            return settings.YMIN

    def get_ymax(self, subplot, subplots):
        if settings.YMAX is None:
            return max([sp.df[sp.var].max() for sp in subplots
                        if self.is_in_same_plot(sp, subplot)]) * 1.01
        else:
            return settings.YMAX

    def get_vmin(self, subplot, subplots):
        if settings.VMIN is None:
            return min([sp.df[sp.var].min() for sp in subplots
                        if self.is_in_same_plot(sp, subplot)])
        else:
            return settings.VMIN

    def get_vmax(self, subplot, subplots):
        if settings.VMAX is None:
            return max([sp.df[sp.var].max() for sp in subplots
                        if self.is_in_same_plot(sp, subplot)])
        else:
            return settings.VMAX

    def is_in_same_plot(self, sp, subplot):
        return (
            not settings.ROW_RANGES or (sp.irow == subplot.irow)
        ) and (
            not settings.COLUMN_RANGES or (sp.icol == subplot.icol)
        )
