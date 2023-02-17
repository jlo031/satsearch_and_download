# Satellite Products Search & Download

This library provides python code for search and batch download of various satellite products. It currenlty supports Sentinel-1 (EW GRD), Sentinel-2 (L1C), and Sentinel-3 (OLCI). The search is done via `SentinelAPI` on Copernicus SciHub. Download is done through Creodias, to avoid issues with archived products.


### Requirements

- [Copernicus SciHub] account user account on Copernicus Open Access Hub
- [Creodias] account user account on Creodias


### Conda environment
It is recommended to setup a virtual conda environment to install this library. Create a virtual environment called 'satsearch' and install required packages like this (tested on Ubuntu22.04 February 17th 2023):

    # create new environment
    conda create -y -n satsearch python=3.7 ipython dateparser loguru python-dotenv

    # activate environment
    conda activate satsearch
    
    # install required packages
    pip install sentinelsat geojson shapely
    conda install -c anaconda requests
    conda install -c conda-forge python-keycloak


### Installation

Start by cloning the repository:

    # clone the repository
    git clone https://github.com/jlo031/satsearch_and_download.git

Now, change into the main directory of the cloned repository (it should contain the 'setup.py' file) and install the library by running:

    # installation
    pip install .



### Usage

The library requires access to your user accounts on copernicus scihub and on creodias. You must provide your login details to be stored in a local _.env. file. In your working directory, create a file called `.env` that contains the following lines:
    
>DHUS_USER='your-scihub-username'  
>DHUS_PASSWORD='your-scihub-password'  
>CREO_USER='your-creodias-username'  
>CREO_PASSWORD='your-creodias-password'





[Copernicus SciHub]: https://scihub.copernicus.eu/dhus/#/home
[Creodias]:https://creodias.eu/
