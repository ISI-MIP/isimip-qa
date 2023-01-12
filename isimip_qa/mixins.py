from .config import settings


class SVGPlotMixin(object):

    def get_path(self, datasets, place, time_step):
        dataset = datasets[0]
        path = dataset.replace_name(region=place, time_step=time_step, **settings.SPECIFIERS)
        return settings.ASSESSMENTS_PATH.joinpath(path.name).with_suffix('.svg')


class GridPlotMixin(object):

    def get_grid(self):
        g = [1, 1]
        for d, j in enumerate([1, 0]):
            if settings.GRID > j:
                try:
                    identifier = settings.IDENTIFIERS[j]
                    g[d] = len(settings.SPECIFIERS[identifier])
                except IndexError:
                    pass
        return g

    def get_grid_indexes(self, i):
        gi = [0, 0]
        for d, j in enumerate([1, 0]):
            if settings.GRID > j:
                try:
                    identifier = settings.IDENTIFIERS[j]
                    specifier = settings.PERMUTATIONS[i][j]
                    gi[d] = settings.SPECIFIERS[identifier].index(specifier)
                except IndexError:
                    pass
        return gi

    def get_title(self, i):
        t = []
        for j in [1, 0]:
            if settings.GRID > j:
                try:
                    t.append(settings.PERMUTATIONS[i][j])
                except IndexError:
                    pass
        return ' '.join(t)

    def get_label(self, i):
        return ' '.join(settings.PERMUTATIONS[i][settings.GRID:])
