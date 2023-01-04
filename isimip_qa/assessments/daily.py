import matplotlib.pyplot as plt
import pandas as pd

from ..extractions import PointExtraction
from ..models import Assessment


class DayAssessment(Assessment):

    def plot(self):
        variable = self.dataset.specifiers['variable']
        extraction = PointExtraction(self.dataset)

        for place, lat, lon in extraction.points:
            csv_path = extraction.get_csv_path(place)
            svg_path = self.get_svg_path(place)

            if not csv_path.exists():
                extraction.extract()

            if not svg_path.exists():
                df = pd.read_csv(csv_path, index_col='time', parse_dates=['time'], infer_datetime_format=True)

                fig = plt.figure(figsize=(20, 10))
                plt.plot(df.index, df[variable])
                plt.title(svg_path.name)
                plt.xlabel('day')
                plt.ylabel(f'mean {variable}')
                fig.savefig(svg_path, bbox_inches='tight')

    def get_svg_path(self, place):
        region = self.dataset.specifiers['region']
        path_str = str(self.dataset.path).replace(f'_{region}_', f'_{place}_')
        return self.dataset.output_path.joinpath(path_str).with_suffix('.svg')
