import xarray as xr

from ..models import Extraction


class PointExtraction(Extraction):

    points = [
        ('berlin', 52.395833, 13.061389),
        ('cairo', 30.056111, 31.239444),
        ('jakarta', -6.175, 106.828611)
    ]

    def extract(self):
        for file_path in self.dataset.files:
            ds = xr.load_dataset(file_path)
            for place, lat, lon in self.points:
                df = ds.sel(lat=lat, lon=lon, method='nearest').to_dataframe()

                csv_path = self.get_csv_path(place)
                if not csv_path.exists():
                    df.to_csv(csv_path)
                else:
                    df.to_csv(csv_path, mode='a', header=False)

    def get_csv_path(self, place):
        region = self.dataset.specifiers['region']
        path_str = str(self.dataset.path).replace(f'_{region}_', f'_{place}_')
        return self.dataset.output_path.joinpath(path_str).with_suffix('.csv')
