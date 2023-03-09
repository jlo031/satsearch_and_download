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
    pip install sentinelsat geojson shapely chardet
    conda install -c anaconda requests
    conda install -c conda-forge python-keycloak


### Installation

Start by cloning the repository:

    # clone the repository
    git clone git@github.com:jlo031/satsearch_and_download.git
    
    Now, change into the main directory of the cloned repository (it should contain the 'setup.py' file) and install the library by running:

    # installation
    pip install .



### User credential setup

The library requires access to your user accounts on copernicus scihub and on creodias. You must save your credentials in a local _.env._ file. In your working directory, create a file called `.env` that contains the following lines:
    
>DHUS_USER='your-scihub-username'  
>DHUS_PASSWORD='your-scihub-password'  
>CREO_USER='your-creodias-username'  
>CREO_PASSWORD='your-creodias-password'

For more information see [python-dotenv] package.


### Usage

#### 1) Search for satellite products
The search module offers the _find_sentinel_products_ function, which requires the following positional arguments:
```
find_sentinel_products(sensors, area, starttime, endtime)
```
The search funtion uses the _sentinelAPI_ query from the _sentinelsat_ package. For further customization refer to [copernicus API query].

#### 2) Batch download
The download module offers two funtions: _read_txt_file_to_list_ and _download_products_from_list_.
```
read_txt_file_to_list(txt_path)
download_products_from_list(product_list, download_dir)
```
See docstrings for further information and keyword arguments.




[Copernicus SciHub]: https://scihub.copernicus.eu/dhus/#/home
[Creodias]:https://creodias.eu/
[python-dotenv]:https://pypi.org/project/python-dotenv/

[copernicus API query]:https://scihub.copernicus.eu/twiki/do/view/SciHubUserGuide/FullTextSearch?redirectedfrom=SciHubUserGuide.3FullTextSearch
