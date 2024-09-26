# Biocarbon Near Real Time Data Visualization

This repo contains Jupyter Notebooks to visualize the real time data from the autonomy assets deployed during the two BioCarbon cruises.

An HTML version of the notebook is produced every day and made available for everyone. But if you need to play yourself with the data and the plot the following instructions will guide you to set up a working environment to run the notebooks.

## Python installation

We recommand to first check your python installation on your computer, and to update it if needed. In a terminal, type :

```
python -V
```

If python is a version lower than Python 3.12, consider updating python from the [python download page](https://www.python.org/downloads/).

## Jupyter Notebook using VSCode

To easily use jupyter notebooks I recommend using [VSCode](https://code.visualstudio.com/), as it support multiple languages, has a version control interface and different terminal integrated (We will use bash here).

## Repo installation

Then you can clone the repo, using a github gui or by running either (for SSH)

```
git clone git@github.com:NOC-OBG-Autonomy/biocarbon_nrt_data_viz.git
```
or (for HTTPS)
```
git clone https://github.com/NOC-OBG-Autonomy/biocarbon_nrt_data_viz.git
```

## Python environment

The best practice to work with python is to create virtual environment or conda environment. Create one by running 

```
python -m venv nrt_autonomy_env
```

You can then activate your venv by typing for windows users :

```
nrt_env/Scripts/activate
```
and for Mac/Unix users
```
source nrt_env/bin/activate
```
From there, all the libraries you will install will be install in this environment and won't interfer with your potential other python project that use an older/newer version of those liraries.

This repo has a requirement.txt file that indicates all the libraries needed to run the notebook. Just run 

```
pip install -r "requirements.txt"
```

And you're all set up !

## Running the notebook

The main notebook is Python_notebooks/autonomy_visualization.ipynb
Open it on VSCode and you can either run it entirely or cell by cell. The first part download the latest data of gliders and float, and the next part make some plots. VSCode will ask you to select a python kernel, you must select nrt_env here. 
A data folder will be created and filled in with the data, you don't need to provide any inputs, except if you don't want to save the data in the repo folder.

## Contributing

If you want to improve this little project you are very welcome to make some PR. If you changed the name of the venv please add it to the gitignore before.
You can also open issues if you want more feature and bug corrections. 
