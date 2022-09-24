from os import stat, terminal_size
from typing import Dict

from pandas.core.frame import DataFrame
from .Baseloader import BaseloaderClass

import pandas as pd

station_info = {
    'Joya': {
        'Lenght': 17713,
        'Start Date': "1965-11-01",
        'End Date': "2014-4-30",
    },
    'Majes': {
        'Lenght': 10865,
        'Start Date': "1984-08-01",
        'End Date': "2014-04-30",
    },
    "Pampilla": {
        'Lenght': 8165,
        'Start Date': "1992-01-01",
        'End Date': "2014-04-30",
    },
    "Chiguata": {
        'Lenght': 6721,
        'Start Date': "1995-12-06",
        'End Date': "2014-04-30",
    }
}


class AqpLoader(BaseloaderClass):
    def __init__(self, path='../api/Datos') -> None:
        self.stations = ["Joya", "Chiguata", "Majes", "Pampilla"]
        self.features = ['precipitation', 'tempMax', 'tempMin']
        self.path = path

    def get_metadata(self):
        meta_data = []

        for station in self.stations:

            station_data = {
                "station_name": station,
                "features": ["Precipitation", "Temp. Min", "Temp. Max"],
                "null_per": {
                    "Precipitation": 0.20,
                    "Temp. Min": 0.46,
                    "Temp. Max": 0.39
                },
                "info": station_info[station],
            }
            meta_data.append(station_data)
        return meta_data

    def get_station_metadata(self, station) -> Dict:

        station_data = {
            "station_name": station,
            "features": ["Precipitation", "Temp. Min", "Temp. Max"],
            "null_per": {
                "Precipitation": 0.20,
                "Temp. Min": 0.46,
                "Temp. Max": 0.39
            },
            "info": station_info[station],
        }
        return station_data

    def get_station_df(self, station):
        print("Stationasds:", station)
        if station.lower() not in [i.lower() for i in self.stations]:
            return None
        station_file: DataFrame = pd.read_csv(
            f"{self.path}/{station.lower()}.txt", sep=' ', parse_dates={"date": [0, 1, 2]})

        station_file.columns = ['date'] + self.features
        # station_file['date'] = station_file['date']
        # station_file['date'] = pd.to_datetime(station_file['date'])

        station_file.set_index('date', inplace=True)
        station_file.index = station_file.index.strftime("%Y-%m-%d")

        return station_file[:1000]
    
    def get_station_df_indexed(self, station):
        if station.lower() not in [i.lower() for i in self.stations]:
            return None
        station_file: DataFrame = pd.read_csv(
            f"{self.path}/{station.lower()}.txt", sep=' ', parse_dates={"date": [0, 1, 2]})

        station_file.columns = ['date'] + self.features

        station_file.set_index('date', inplace=True)

        return station_file[:1000]

    def get_data(self, station, to_json=True, with_df=False) -> Dict:
        if station.lower() not in [i.lower() for i in self.stations]:
            return None, None
        else:
            station_df = self.get_station_df(station)
            if to_json:
                return station_df.reset_index().to_json(orient='records', index=True), station_df
            return station_df.to_dict(orient='records'), station_df

    def get_station_datadiff(self, station) -> int:
        station_df: DataFrame = self.get_data_df(station)
        return station_df.max() - station_df.min()
