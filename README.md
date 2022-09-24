# VisWeb

## Note:

New API now requires HDF5 to work. You can download it [here](https://www.hdfgroup.org/downloads/hdf5).

## Changelog

- Now Using HDF5 to read Madrid .h5 file

## TODO:

- [x] Improve the method to keep changes on visualization
- [x] Complete Fourier Analysis of cyclicity
- [x] Complete data filter: weekly, monthly (currently not included in this version)
- [x] Show progress bar when load data
- [x] Show message to make sure the quality of Data
- [x] Add original data
- [x] Put max points in ciclicity operator
- [x] Add spiral graph to ciclicity
- [ ] Close an operator
- [x] Feature discovery

## BUGS:

- [x] Past and Future Tables names and actions
- [x] Dim. Red changes dropdown of features
- [x] Return to kpadding breaks everything


## Run the new API server
To run the new API server you should extract the [Datasets.zip](https://drive.google.com/drive/folders/1HACDggmL6esVgKEJYEBsGHOyj7Qd_98k?usp=sharing) at /new_api/Datasets

then go to the new_api folder and install dependencies:

`cd new_api && pip3 install -r requirements.txt`

Then, start the server with:

`python3 main.py`



## Run the API server

Before this, you should extract the .rar file `Datos.rar`

Go to the api folder and install dependencies:

`cd api && pip3 install -r requirements.txt`

Then, start the server with:

`python3 main.py`

## Run the Client

Go to the web folder and install dependencies with:

`cd web && npm install`

Then, start the client with:

`npm run serve`
