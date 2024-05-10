import pandas as pd
import matplotlib.pyplot as plot
import numpy as np
import polars as pl
import requests
from urllib.request import urlretrieve
import plotting_functions as fn
import os
import yaml
 
workdir = os.getcwd()

config_file = workdir + '/Plotting_tools/config.yml'
config_link = open(config_file, 'r')
config = yaml.safe_load(config_link)

paths = config['directories-paths']

#download the bio index file, which provide dac paths for downloading float data
float_wmo = config['floats_wmo']

fn.create_missing_directories()
fn.download_float_synth_file(paths['host'], 'Data/Floats/synth.txt')

index_table = pl.read_csv('Data/Floats/synth.txt', skip_rows=8)

# Mutate a new column based on the regular expression extraction
index_table = index_table.with_columns(
    pl.col('file').map_elements(lambda x: fn.extract_digits(x), return_dtype=pl.Utf8).alias('wmo')
)

wmo_table = index_table.filter(pl.col('wmo') == float_wmo)

#downlaod floats data
dac_name = wmo_table['file'][0].split('/', 1)[0]
local_argo_directory = 'Data/Floats'
dac = paths['dac']


download_url = dac + '/' + dac_name + '/' + float_wmo + '/' + float_wmo + '_Sprof.nc'

filename = local_argo_directory + '/' + download_url.rsplit('/', 1)[1]
urlretrieve(download_url, filename)


#ploat the float traj

#ploat the float temp

#plot the float sal

#plot the mld ts

#plot the chla

#plot the bbp

#plot the oxygen