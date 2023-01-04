import matplotlib.pyplot as plt
import pandas as pd

from ..extractions import PointExtraction
from ..models import Assessment


class DayOfYearlyAssessment(Assessment):

    def plot(self):
        variable = self.dataset.specifiers['variable']
        extraction = PointExtraction(self.dataset)

        for place, lat, lon in extraction.points:
            csv_path = extraction.get_csv_path(place)
            svg_path = self.get_svg_path(place)

            if not csv_path.exists():
                extraction.extract()

            if not svg_path.exists():
                df = pd.read_csv(csv_path, index_col='time', parse_dates=['time'], infer_datetime_format=True) \
                       .groupby(lambda x: x.dayofyear).mean()

                fig = plt.figure(figsize=(20, 10))
                plt.step(df.index, df[variable], where='mid')
                plt.title(svg_path.name)
                plt.xlabel('day of year')
                plt.ylabel(f'mean {variable}')
                fig.savefig(svg_path, bbox_inches='tight')

    def get_svg_path(self, place):
        region = self.dataset.specifiers['region']
        time_step = self.dataset.specifiers['time_step']
        path_str = str(self.dataset.path).replace(f'_{region}_', f'_{place}_') \
                                         .replace(f'_{time_step}', '_dayofyearly')
        return self.dataset.output_path.joinpath(path_str).with_suffix('.svg')
