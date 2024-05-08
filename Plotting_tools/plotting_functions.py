def extract_digits(text):
    match = re.search(r'\d+', text)
    return match.group() if match else 0

def create_missing_directories():
    """Create a data and plot folders if they are missing
    """    
    # Define the path to the parent directory
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

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

def download_float_synth_file(hostname, data_directory):
    """Download the BGC Argo synthetic file index

    Args:
        hostname (string): The URL of a synth file host (e.g. 'https://data-argo.ifremer.fr/argo_synthetic-profile_index.txt')
        data_directory (_type_): The data folder were the 'synth_file.txt' will be written
    """    
    response = requests.get(hostname, stream=True)

    Synth_path = data_directory + 'Data/synth_file.txt'

    with open(destination, "wb") as f:
        r = requests.get(host)
        f.write(r.content)

def download_float_nc(wmo_list, synth_file, data_directory, floats_directory = 'Data/Floats'):
    index_table = pl.read_csv(synth_file, skip_rows=8)
    index_table = index_table.with_columns(
    pl.col('file').map_elements(lambda x: extract_digits(x), return_dtype=pl.Utf8).alias('wmo'))

    for wmo in wmo_list:
        wmo_table = index_table.filter(pl.col('wmo') == wmo)
        dac_name = wmo_table['file'][0].split('/', 1)[0]
        download_url = dac + '/' + dac_name + '/' + wmo + '/' + wmo + '_Sprof.nc'
        filename = wmo_directory + '/' + download_url.rsplit('/', 1)[1]
        urlretrieve(download_url, filename)
        print(wmo + ' NCDF file downloaded')


    