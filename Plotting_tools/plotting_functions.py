import pandas as pd
import numpy as np
import requests
import shutil
import os
import gzip
from pathlib import Path
import re
from tqdm import tqdm
from urllib.request import urlretrieve
import xarray as xr
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import seaborn as sns
from glob import glob
from datetime import datetime
from scipy import interpolate

def extract_digits(text):
    match = re.search(r'\d+', text)
    return match.group() if match else 0

def create_missing_directories(wmo, varlist):
    import os
    """Create a data and plot folders if they are missing
    """    
    # Define the path to the parent directory
    parent_dir = os.path.abspath(os.getcwd())

    # Check if 'data' folder exists in the parent directory
    data_dir = os.path.join(parent_dir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print("'data' folder created in the parent directory.")
    else:
        print("'data' folder already exists in the parent directory.")

    # Check if 'floats' directory exists inside 'data' folder
    floats_dir = os.path.join(data_dir, 'Floats')
    if not os.path.exists(floats_dir):
        os.makedirs(floats_dir)
        print("'floats' directory created inside 'data' folder.")
    else:
        print("'floats' directory already exists inside 'data' folder.")

    # Check if 'gliders' directory exists inside 'data' folder
    gliders_dir = os.path.join(data_dir, 'Gliders')
    if not os.path.exists(gliders_dir):
        os.makedirs(gliders_dir)
        print("'gliders' directory created inside 'data' folder.")
    else:
        print("'gliders' directory already exists inside 'data' folder.")

    # Check if 'output' folder exists in the parent directory
    output_dir = os.path.join(parent_dir, 'Output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("'Output' folder created in the parent directory.")
    else:
        print("'Output' folder already exists in the parent directory.")
    # Check if 'Plots' folder exists in the parent directory
    plot_dir = os.path.join(output_dir, 'Plots')
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
        print("'Plots' folder created in the Output directory.")
    else:
        print("'Plots' folder already exists in the Output directory.")
    # Check if wmo folder exists in the parent directory
    wmo_dir = os.path.join(plot_dir, wmo)
    if not os.path.exists(wmo_dir):
        os.makedirs(wmo_dir)
        print(wmo + " folder created in the Plots directory.")
    else:
        print(wmo + "folder already exists in the Plots directory.")
    for var in varlist:
        var_dir = os.path.join(wmo_dir, var)
        if not os.path.exists(var_dir):
            os.makedirs(var_dir)
            print(var + " folder created in the " + wmo +  " directory.")
        else:
            print(var +  " folder already exists in the " + wmo +  " directory.")

def download_float_synth_file(hostname, data_directory):
    """Download the BGC Argo synthetic file index

    Args:
        hostname (string): The URL of a synth file host (e.g. 'https://data-argo.ifremer.fr/argo_synthetic-profile_index.txt')
        data_directory (_type_): The data folder were the 'synth_file.txt' will be written
    """    
    response = requests.get(hostname, stream=True)

    Synth_path = data_directory + 'Data/synth_file.txt'

    with open(data_directory, "wb") as f:
        r = requests.get(hostname)
        f.write(r.content)

def download_float_nc(wmo_list, synth_file, data_directory, floats_directory = 'Data/Floats'):
    index_table = pl.read_csv(synth_file, skip_rows=8)
    index_table = index_table.with_columns(
    pl.col('file').map_elements(lambda x: extract_digits(x), return_dtype=pl.Utf8).alias('wmo'))

    for wmo in wmo_list:
        wmo_table = index_table.filter(pl.col('wmo') == wmo)
        dac_name = wmo_table['file'][0].split('/', 1)[0]
        download_url = dac + '\\' + dac_name + '\\' + wmo + '\\' + wmo + '_Sprof.nc'
        filename = wmo_directory + '/' + download_url.rsplit('/', 1)[1]
        urlretrieve(download_url, filename)
        print(wmo + ' NCDF file downloaded')

def load_bathymetry(zip_file_url):
    """Read zip file from Natural Earth containing bathymetry shapefiles"""
    # Download and extract shapefiles
    import io
    import zipfile

    r = requests.get(zip_file_url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(bath_directory)

    # Read shapefiles, sorted by depth
    shp_dict = {}
    files = glob(bath_directory + '*.shp')
    assert len(files) > 0
    files.sort()
    depths = []
    for f in files:
        depth = '-' + f.split('_')[-1].split('.')[0]  # depth from file name
        depths.append(depth)
        bbox = (min_lon - 3, max_lon + 3,min_lat - 1, max_lat + 1)  # (x0, y0, x1, y1)
        nei = shpreader.Reader(f, bbox=bbox)
        shp_dict[depth] = nei
    depths = np.array(depths)[::-1]  # sort from surface to bottom
    return depths, shp_dict

def open_floatnc(wmo, varlist):
    """Retrun a pandas dataframe from the Sprof NC of the wmo provided

    Args:
        wmo (str): Float WMO

    Returns:
        pandas dataframe: a df with all the float variables necessary to plotting
    """    
    float_filename = 'Data/Floats/' + wmo + '_Sprof.nc'
    dat = xr.open_dataset(float_filename)
    varlist.append('JULD')
    varlist.append('PRES')
    df = dat[varlist].to_dataframe()
    dat.close()
    df = df.reset_index().set_index('JULD', drop=False)
    return df

def plot_profile(data, varname, xmax, float_wmo, pres_adjusted):

    import math
    last_date = max(data['JULD'])

    last_df = data[data['JULD'] == last_date]
    early_df = data[data['JULD'] != last_date]

    
    if pres_adjusted == True:
        if len(early_df.index) > 0 :
            alphas = (early_df['N_PROF'] + 1 - min(early_df['N_PROF']) + 1)/(max(early_df['N_PROF']) + 1 - min(early_df['N_PROF']) + 1)

            fig = plt.figure(figsize=(20, 10))
            ax = fig.add_subplot()

            sc2 = ax.scatter( early_df[varname], - (early_df['PRES_ADJUSTED']), alpha = alphas, c = 'grey')
            sc = ax.scatter( last_df[varname], - (last_df['PRES_ADJUSTED']), c = 'black')

            ax.set_xlim(0, xmax)

            # set the plot title
            ax.set_title('Float wmo : ' + float_wmo + "\n" + varname + " profile : " + last_date.strftime("%Y-%m-%d %H:%M:%S"))
        else :
            fig = plt.figure(figsize=(20, 10))
            ax = fig.add_subplot()

            sc = ax.scatter( last_df[varname], - (last_df['PRES_ADJUSTED']), c = 'black')
            ax.set_xlim(0, xmax)
            ax.set_title('Float wmo : ' + float_wmo + "\n" + varname + "first profile : " + last_date.strftime("%Y-%m-%d %H:%M:%S"))
        #set the plot filename
        filename = 'Output/Plots/' + float_wmo + '/' + varname + '/' + str(last_df['N_PROF'].unique()[0]) + '_' + float_wmo + '_' + varname + '.png'
    else:
        if len(early_df.index) > 0 :
            alphas = (early_df['N_PROF'] + 1 - min(early_df['N_PROF']) + 1)/(max(early_df['N_PROF']) + 1 - min(early_df['N_PROF']) + 1)

            fig = plt.figure(figsize=(20, 10))
            ax = fig.add_subplot()

            sc2 = ax.scatter( early_df[varname], - (early_df['PRES']), alpha = alphas, c = 'grey')
            sc = ax.scatter( last_df[varname], - (last_df['PRES']), c = 'black')

            ax.set_xlim(0, xmax)
            ax.set_ylim(-250, 0)

            # set the plot title
            ax.set_title('Float wmo : ' + float_wmo + "\n" + varname + " profile : " + last_date.strftime("%Y-%m-%d %H:%M:%S"))
        else :
            fig = plt.figure(figsize=(20, 10))
            ax = fig.add_subplot()

            sc = ax.scatter( last_df[varname], - (last_df['PRES']), c = 'black')
            ax.set_xlim(right = xmax)
            ax.set_title('Float wmo : ' + float_wmo + "\n" + varname + "first profile : " + last_date.strftime("%Y-%m-%d %H:%M:%S"))
        #set the plot filename
        filename = 'Output/Plots/' + float_wmo + '/' + varname + '/' + str(last_df['N_PROF'].unique()[0]) + '_' + float_wmo + '_' + varname + '.png'
    print(filename)
    plt.savefig(filename)
    plt.close()

    