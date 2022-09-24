from os import stat
from pandas.core.frame import DataFrame
import h5py
import pandas as pd
from typing import Dict

import numpy as np

from .Baseloader import BaseloaderClass


class MadridLoader(BaseloaderClass):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        print('Dataloader construct called: ', path)
        self.data: pd.DataFrame = None
        self.read()
        # with pd.HDFStore(self.path) as data:
        #     stations = data.keys()
        self.stations = list(map(lambda x: x[1:], self.stations[:-1]))

    def get_metadata(self):
        meta_data = []
        for station in self.stations:
            station_df = self.data[station]
            null_p = station_df.isnull().sum() * 100 / len(station_df)

            station_data = {
                "station_name": station,
                "features": list(station_df.columns),
                "null_per": null_p.to_dict(),
                "info": {
                    "Length": len(station_df),
                    "Start date": station_df.index.min().strftime("%Y-%m-%d"),
                    "End date": station_df.index.max().strftime("%Y-%m-%d")
                },
            }
            meta_data.append(station_data)
        return meta_data

    def get_station_datadiff(self, station) -> int:
        station_df = self.data[station]
        return station_df.max() - station_df.min()

    def get_station_metadata(self, station) -> Dict:
        station_df = self.data[station]
        null_p = station_df.isnull().sum() * 100 / len(station_df)
        station_data = {
            "station_name": station,
            "features": list(station_df.columns),
            "null_per": null_p.to_dict(),
            "info": {
                "Length": len(station_df),
                "Start date": station_df.index.min().strftime("%Y-%m-%d"),
                "End date": station_df.index.max().strftime("%Y-%m-%d")
            },
        }
        return station_data

    def read(self):
        # with pd.HDFStore(self.path) as data:
        #     pd_data = data
        store = pd.HDFStore(self.path, mode='r')
        self.data = store
        self.stations = self.data.keys()

    def read_station_data(self, station_id):
        resample = 'D'
        station_data = self.data[station_id]
        station_data = station_data.resample(resample).agg(np.mean)
        station_data.index = station_data.index.strftime("%Y-%m-%d")
        # station_data.index = pd.to_datetime(station_data.index)

        station_data = station_data[:1000]
        return station_data

    def get_station_df(self, station_id):
        return self.read_station_data(station_id)

    def get_station_df_indexed(self, station_id):
        resample = 'D'
        station_data = self.data[station_id]
        station_data = station_data.resample(resample).agg(np.mean)
        station_data.index = station_data.index.strftime("%Y-%m-%d")
        station_data.index = pd.to_datetime(station_data.index)

        station_data = station_data[:1000]
        return station_data

    def get_data(self, station_id="28079016", to_json=True, with_df=False):
        if self.data is None:
            self.read()

        station_data: DataFrame = self.get_station_df(station_id)
        json_res = None
        if to_json:
            json_res = station_data.reset_index().to_json(orient='records')
        else:
            json_res = station_data.to_dict(orient='records')
        return json_res, station_data


if __name__ == '__main__':
    path = '../Datasets/Madrid/madrid.h5'
    ml: MadridLoader = MadridLoader(path)
    # print(ml.get_metadata())
    # print(ml.get_data())
    pass


# with pd.HDFStore(path) as data:
#     test = data['28079016']

# test.rolling(window=24).mean().plot(figsize=(20, 7), alpha=0.8)


# keys = ['28079001', '28079003', '28079004', '28079006', '28079007', '28079008', '28079009', '28079011', '28079012', '28079014', '28079015', '28079016', '28079017', '28079018', '28079019', '28079021', '28079022', '28079023', '28079024', '28079025', '28079026', '28079027', '28079035', '28079036', '28079038', '28079039', '28079040', '28079047', '28079048', '28079049', '28079050', '28079054', '28079055', '28079056', '28079057', '28079058', '28079059', '28079060', '28079099', 'master']
# f = h5py.File(path, 'r')
# for k in f.keys():
#     print('{}: {}'.format(k, ', '.join(e.decode('utf-8') for e in f['28079016']['block0_items'])))
