import logging
import sys
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

        plt.rcParams.update({'mathtext.default': 'regular'})

        logger.info(f'write {path}')
        try:
            fig.savefig(path)
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
    max_dimensions = sys.maxsize

    def __init__(self, *args, path=None, dimensions=None, grid=0, figs=0, **kwargs):
        self.path = Path(path) if path else None
        self.dimensions = dimensions
        self.grid = grid
        self.figs = figs
        self.styles = {}

        if self.dimensions:
            self.dimensions_keys = list(self.dimensions.keys())
            self.dimensions_values = list(self.dimensions.values())
            self.dimensions_len = len(self.dimensions_keys)
            self.permutations = list(product(*self.dimensions_values))
            self.figs = max(self.figs, self.dimensions_len - self.grid - self.max_dimensions)

        super().__init__(*args, **kwargs)

    def get_figure(self, nrows, ncols, ratio=1):
        fig, axs = plt.subplots(nrows, ncols, squeeze=False, figsize=(6 * ratio * ncols, 6 * nrows),
                                constrained_layout=True)
        for ax in chain.from_iterable(axs):
            ax.tick_params(bottom=False, labelbottom=False, left=False, labelleft=False)
        return fig, axs

    def get_figure_path(self, ifig=0):
        if self.path is None:
            return None

        if not self.path.suffix:
            self.path = self.path.with_suffix('.' + settings.PLOTS_FORMAT)

        stem = self.path.stem
        suffix = self.path.suffix

        if self.dimensions:
            placeholders = {}

            for j, key in enumerate(self.dimensions_keys):
                if (j < self.grid) or (j < self.dimensions_len - self.figs):
                    # for the first dimensions, which are not figure dimensions, combine the values
                    primary_values = [value for value in self.dimensions_values[j] if value in settings.PRIMARY]
                    if primary_values:
                        values_strings = primary_values
                    elif len(self.dimensions_values[j]) < 10:
                        values_strings = self.dimensions_values[j]
                    else:
                        values_strings = ['various']
                else:
                    # for the last self.figs dimensions, which generate seperate figures, take seperate values
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

        return settings.PLOTS_PATH / self.path.with_name(stem).with_suffix(suffix)

    def get_grid(self):
        grid = [1, 1, 1]

        if self.dimensions:
            for j, key in enumerate(self.dimensions_keys):
                ndim = len(self.dimensions[key])

                if j < self.grid:
                    # the grid dimensions generate rows and columns
                    grid[j] = ndim
                elif (j >= self.dimensions_len - self.figs):
                    # the last self.figs dimensions multiply the number of seperate figures
                    grid[-1] *= len(self.dimensions_values[j])

        return reversed(grid)

    def get_grid_indexes(self, i):
        grid_indexes = [0, 0, 0]

        if self.dimensions:
            permutation = self.permutations[i]

            for j, key in enumerate(self.dimensions_keys):
                value = permutation[j]
                value_index = self.dimensions[key].index(value)

                if j < self.grid:
                    # the first dimensions indicate the column and the row
                    grid_indexes[j] = value_index
                elif self.figs > 0:
                    # the figure index is computed like this:
                    # lets assume self.figs = 3 and i3,i2,i1 are the indexes of dimensions d3,d2,d1
                    # the figure index is i1 + i2 * len(d1) + i3 * len(d1) * len(d2)
                    if j == self.dimensions_len - 1:
                        # the last value_index just adds to the figure index
                        grid_indexes[-1] += value_index
                    elif j >= self.dimensions_len - self.figs:
                        # the other value_indexes need be multiplied by the lenghts of the dimensions to the right
                        for values in self.dimensions_values[j+1:]:
                            value_index *= len(values)
                        grid_indexes[-1] += value_index

        return reversed(grid_indexes)

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

            primary = self.get_primary(index)

            if primary:
                color, linestyle, marker = self.get_style(index)
            else:
                color = 'gray'
                linestyle = '-'
                marker = '.'

            subplot = Subplot(
                df=df,
                attrs=attrs,
                var=var,
                label=self.get_label(index) if primary else None,
                title=self.get_title(index) if primary else None,
                color=color,
                linestyle=linestyle,
                marker=marker,
                zorder=10 if primary else 0,
                ifig=ifig,
                irow=irow,
                icol=icol,
                primary=primary
            )

            subplots.append(subplot)

        return subplots

    def get_df(self, dataset):
        raise NotImplementedError

    def get_attrs(self, dataset):
        raise NotImplementedError

    def get_primary(self, i):
        if self.dimensions and settings.PRIMARY:
            permutation = self.permutations[i]

            for j, key in enumerate(self.dimensions_keys):
                if permutation[j] in settings.PRIMARY:
                    return True

            return False
        else:
            return True

    def get_title(self, i):
        if self.dimensions:
            return ' '.join(self.permutations[i][:self.grid])

    def get_label(self, i):
        if self.dimensions:
            return ' '.join(self.permutations[i][self.grid:])

    def get_style(self, i):
        if self.dimensions:
            if self.figs > 0:
                label = self.permutations[i][self.grid:-self.figs]
            else:
                label = self.permutations[i][self.grid:]

            if label not in self.styles:
                index = len(self.styles.keys())
                color_index = index % len(self.colors)
                linestyle_index = int(index / len(self.colors)) % len(self.linestyles)
                marker_index = int(index / len(self.colors)) % len(self.markers)
                self.styles[label] = (
                    self.colors[color_index],
                    self.linestyles[linestyle_index],
                    self.markers[marker_index]
                )
            return self.styles[label]
        else:
            return self.colors[0], self.linestyles[0], self.markers[0]

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
