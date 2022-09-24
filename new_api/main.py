from os import stat
from re import S
from typing import Dict, List
import bottle
from bottle import request, response, route, static_file, view

import json
from pandas.core.frame import DataFrame
from pandas.io.parsers import read_csv
import simplejson
import h5py

import pandas as pd
import statsmodels.api as sm
import numpy as np

from matplotlib.pyplot import table
from scipy import fft
from scipy import signal as sig
from sklearn.decomposition import PCA
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer, KNNImputer, SimpleImputer
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from Dataloader.Baseloader import BaseloaderClass
from Dataloader.MadridLoader import MadridLoader
from Dataloader.IndiaDataloader import IndiaDataloader
from Dataloader.AqpLoader import AqpLoader
from helpers import get_period_days

m_path = './Datasets/Madrid/madrid.h5'
i_path = './Datasets/India/station_day.csv'
ml = MadridLoader(m_path)
il = IndiaDataloader(i_path)
aqpl = AqpLoader()


minmax_scaler = MinMaxScaler()
sc_scaler = StandardScaler()


knn_imputer = KNNImputer(missing_values=-1, n_neighbors=10, weights="uniform")
simple_imp = SimpleImputer(missing_values=-1, strategy='mean')
iter_imp = IterativeImputer(
    missing_values=-1, max_iter=20)


def enable_cors(fn):
    def wrapper(*args, **kwargs):
        bottle.response.set_header("Access-Control-Allow-Origin", "*")
        bottle.response.set_header(
            "Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        bottle.response.set_header(
            "Access-Control-Allow-Headers", "Origin, Content-Type")

        # skip the function if it is not needed
        if bottle.request.method == 'OPTIONS':
            return

        return fn(*args, **kwargs)
    return wrapper


loaders: Dict[str, BaseloaderClass] = {
    'madrid': ml,
    'aqp': aqpl,
    'india': il
}

response.headers['Content-Type'] = 'application/json'

current_df: DataFrame = None


@route('/meta_data/<dataset>')
@enable_cors
def meta_data(dataset):
    loader = loaders[dataset]
    return json.dumps(loader.get_metadata())


@route('/meta_data/<dataset>/<station>')
@enable_cors
def station_meta_data(dataset, station):
    loader = loaders[dataset]
    return json.dumps(loader.get_station_metadata(station=station))


@route('/recomendation/<dataset>/<station>')
@enable_cors
def recomendation_by_station(dataset, station):
    loader = loaders[dataset]
    station_metadata = loader.get_station_metadata(station)
    station_df = loader.get_station_df_indexed(station)
    print("DF: ", station_df.info())
    max_period_days = get_period_days(station_df)
    # max_period_days = 0

    recomendations: Dict[str, List[str]] = {
        'Data reduction': [],
        'Quality of Data': [],
        'Variables Behavior': [],
    }

    if len(station_metadata['features']) > 4:
        recomendations['Data reduction'].append('Dim. Red')
    if sum(station_metadata['null_per'].values()) / len(station_metadata['null_per']) > 0.3:
        recomendations['Quality of Data'].append('Clean')
    if max_period_days > 365:
        recomendations['Variables Behavior'].append('Cyclicity')
    if max_period_days <= 365 and max_period_days > 0:
        recomendations['Variables Behavior'].append('Seasonality')


    res = {k: v for k, v in recomendations.items() if len(v) > 0}
    return json.dumps(res)


@route('/data/<dataset>/<station>')
@enable_cors
def data(dataset, station):
    loader = loaders[dataset]
    response.headers['Content-Type'] = 'application/json'
    json_data, df = loader.get_data(station)

    global current_df
    current_df = df
    current_df.fillna(-1, inplace=True)
    print(current_df)
    return json_data


@route('/op/<dataset>/normalize')
@enable_cors
def normalize_dataset(dataset):
    response.headers['Content-Type'] = 'application/json'
    global current_df
    print("current df:", current_df)
    normalized = current_df.apply(lambda x: x/x.max(), axis=0)
    current_df = normalized
    print("normalize:", normalized)
    return normalized.reset_index().to_json(orient='records', index=True)


@route('/op/<dataset>/clean/<method>')
@enable_cors
def clean_dataset(dataset, method):
    response.headers['Content-Type'] = 'application/json'

    global current_df
    data = current_df.values
    # print(data)
    # print(dates)
    data[data < 0] = -1

    if method == 'clean-knn':
        data = knn_imputer.fit_transform(data)
    elif method == 'clean-mean':
        data = simple_imp.fit_transform(data)

    df = pd.DataFrame(data, columns=current_df.columns, index=current_df.index)

    current_df = df
    return df.reset_index().to_json(orient='records', index=True)


@route('/op/<dataset>/transform/<number>')
@enable_cors
def normalize_dataset(dataset, number):
    response.headers['Content-Type'] = 'application/json'

    global current_df
    number = int(number)

    print("current df:", current_df)
    transformed = current_df.apply(
        lambda x: x.astype('float64') * number, axis=0)
    current_df = transformed
    print("transform:", transformed)
    return transformed.reset_index().to_json(orient='records', index=True)


@route('/op/<dataset>/reduce/<n_comp>')
@enable_cors
def reduce_dataset(dataset, n_comp):
    response.headers['Content-Type'] = 'application/json'

    n_comp = int(n_comp)
    pca = PCA(n_comp)
    # dates, data = read_dataset(dataset)
    global current_df
    data = current_df.values
    data[data < 0] = -1
    data = sc_scaler.fit_transform(data)
    data = pca.fit_transform(data)
    df = pd.DataFrame(data, columns=range(1, n_comp+1), index=current_df.index)
    current_df = df
    return df.reset_index().to_json(orient='records', index=True)


@route('/op/<dataset>/vbehavior/<operator>')
@enable_cors
def vbehavior_analyse(dataset, operator):
    response.headers['Content-Type'] = 'application/json'

    global current_df

    data = current_df.values

    data[data < 0] = -1

    if request.query:
        feature = int(request.query.feature)

    dataframe = pd.DataFrame(data, index=pd.DatetimeIndex(current_df.index))

    resample = 'W'

    # If it's not precipitation then use the mean to resample
    if feature > 0:
        res_dataframe = dataframe.resample(resample).mean()[feature]
    # Else use the maxiimum value to resample
    else:
        res_dataframe = dataframe.resample(resample).max()[feature]

    # operator seasonal_decompose
    if operator in ['trend', 'seasonality']:
        decomposition = sm.tsa.seasonal_decompose(
            res_dataframe, model="aditive")
        if operator == 'trend':
            feature_data = decomposition.trend.values
        elif operator == 'seasonality':
            feature_data = decomposition.seasonal.values
        else:
            feature_data = []

    # Fourier
    elif operator == 'cyclicity':
        y = res_dataframe.values
        fourier_output = np.abs(fft.fft(y))
        frecuencies = fft.fftfreq(len(y))
        peaks = sig.find_peaks(fourier_output, prominence=10**2)[0]

        print(peaks)
        peak_freq = frecuencies[peaks]
        peak_power = fourier_output[peaks]

        output = pd.DataFrame()

        output['index'] = peaks
        output['freq (1/hour)'] = peak_freq
        output['amplitude'] = peak_power
        output['period (days)'] = 1/peak_freq
        output['fft'] = fourier_output[peaks]
        output = output.sort_values('amplitude', ascending=False)

        print(output)

        max_amp_index = output['index'].iloc[0:5:2]

        filtered_fft_output = np.array(
            [f if i in max_amp_index.values else 0 for i, f in enumerate(fourier_output)])

        filtered_sig = fft.ifft(filtered_fft_output)
        print("output shape:", filtered_fft_output.shape,
              fourier_output.shape, y.shape)
        feature_data = np.array(filtered_sig.astype('float'))

    feature_data = np.array([feature_data]).T
    feature_data = np.append(feature_data, np.array(
        [res_dataframe.values]).T, axis=1)
    # print(feature_data.shape, res_dataframe.values.shape, feature_data)

    current_df = dataframe
    return dataframe.reset_index().to_json(orient='records', index=True)


@route('/src/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./src')


bottle.run(reloader=True, debug=True)
