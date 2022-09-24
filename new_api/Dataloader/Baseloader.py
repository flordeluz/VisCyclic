from typing import Dict, List

from pandas import DataFrame


class BaseloaderClass:
    def __init__(self, path: str) -> None:
        self.path = path

    def get_data(self, station) -> Dict:
        pass

    def get_metadata(self) -> List:
        pass

    def get_station_metadata(self, station) -> Dict:
        pass

    def get_station_datadiff(self, station) -> int:
        pass
    def get_station_df(self, station) -> DataFrame:
        pass

    def get_station_df_indexed(self, station) -> DataFrame:
        pass

