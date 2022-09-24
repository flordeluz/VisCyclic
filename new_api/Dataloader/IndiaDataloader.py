from typing import Dict
from .Baseloader import BaseloaderClass
import pandas as pd


class IndiaDataloader(BaseloaderClass):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        print('Dataloader construct called: ', path)
        self.data: pd.DataFrame = None
        self.read()
        # with pd.HDFStore(self.path) as data:
        #     stations = data.keys()
        self.stations = list(self.data['StationId'].unique())

    def read(self):
        self.data = pd.read_csv(self.path)
        self.data.drop('AQI_Bucket', axis=1, inplace=True)
        # print(self.data)
        self.stations = self.data.keys()

    def get_metadata(self):
        meta_data = []
        for station in self.stations:
            station_df = self.data[self.data['StationId'] == station]
            null_p = station_df.isnull().sum() * 100 / len(station_df)

            station_data = {
                "station_name": station,
                "features": list(station_df.columns),
                "null_per": null_p.to_dict(),
                "info": {
                    "Length": len(station_df),
                    "Start date": station_df['Date'].min(),
                    "End date": station_df['Date'].max()
                },
            }
            meta_data.append(station_data)
        return meta_data

    def get_station_datadiff(self, station) -> int:
        station_df = self.data[station]
        return station_df.max() - station_df.min()

    def get_station_metadata(self, station) -> Dict:
        station_df = self.data[self.data['StationId'] == station]
        null_p = station_df.isnull().sum() * 100 / len(station_df)

        station_data = {
            "station_name": station,
            "features": list(station_df.columns),
            "null_per": null_p.to_dict(),
            "info": {
                "Length": len(station_df),
                "Start date": station_df['Date'].min(),
                "End date": station_df['Date'].max()
            },
        }

        return station_data

    def get_station_df(self, station_id="AP001"):
        if self.data is None:
            self.read()

        station_data = self.data[self.data['StationId']
                                 == station_id.upper()]
        station_data.drop('StationId', axis=1, inplace=True)
        station_data.rename(columns={'Date':'date'}, inplace=True)
        station_data.set_index('date', inplace=True)
        station_data.index = pd.to_datetime(station_data.index).strftime("%Y-%m-%d")
        # print(station_data.info())
        return station_data[:1000]

    def get_station_df_indexed(self, station_id):
        if self.data is None:
            self.read()

        station_data = self.data[self.data['StationId']
                                 == station_id.upper()][:1000]
        station_data.drop('StationId', axis=1, inplace=True)
        station_data.set_index('Date', inplace=True)
        station_data.index = pd.to_datetime(station_data.index)
        
        return station_data

    def get_data(self, station_id="AP001", to_json=True,  with_df=False):
        if self.data is None:
            self.read()

        station_data = self.get_station_df(station_id)

        if not to_json:
            station_data.set_index('Date', inplace=True)
            return station_data.to_dict(orient='index')
        return station_data.reset_index().to_json(orient='records', index=True), station_data


if __name__ == '__main__':
    path = '../Datasets/India/station_day.csv'

    idData = IndiaDataloader(path)
