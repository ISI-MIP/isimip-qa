from .config import settings


class CSVExtractionMixin(object):

    def get_path(self, dataset, region):
        path = dataset.replace_name(region=region.specifier)
        return settings.EXTRACTIONS_PATH.joinpath(path).with_suffix('.csv')

    def write_csv(self, df, csv_path):
        if csv_path.exists():
            df.to_csv(csv_path, mode='a', header=False)
        else:
            csv_path.parent.mkdir(exist_ok=True, parents=True)
            df.to_csv(csv_path)


class SVGPlotMixin(object):

    def get_path(self, dataset, region, time_step):
        path = dataset.replace_name(region=region.specifier, time_step=time_step, **settings.SPECIFIERS)
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
