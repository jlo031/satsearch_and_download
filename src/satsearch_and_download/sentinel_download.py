# ---- This is <sentinel_download.py> ----

"""
Module to facilitate batch download of Copernicus Sentinel data.
""" 

import os
import sys
import glob
import pathlib

import json
from dotenv import load_dotenv
from loguru import logger
from collections import OrderedDict

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from dateparser import parse

import satsearch_and_download.ssd_helpers as ssdh

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

def read_txt_file_to_list(txt_path):
    """Read product IDs from txt file into list

    Parameters
    ----------
    txt_path : path to txt file with product IDs

    Returns
    -------
    product_list :  list with product name strings
    """

    # open file in read mode
    with open(txt_path,'r') as f:
        product_list = f.read().split("\n")

    # remove potential empties
    while("" in product_list):
        product_list.remove("")


    return product_list

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

def download_products_from_list(
    product_list,
    download_dir,
    overwrite=False,
    loglevel='INFO'
):
    """Download all products from product_list

    Parameters
    ----------
    product_list : list with product name strings
    download_dir : target directory for product download
    overwrite : overwrite already existing products (download again)
    """

    # remove default logger handler and add personal one
    logger.remove()
    logger.add(sys.stderr, level=loglevel)


    # count products
    n_products = len(product_list)
    logger.info(f'Found {n_products} products in product_list')

    # convert folder strings to paths
    download_dir = pathlib.Path(download_dir).expanduser().absolute()
    logger.info(f'download_dir: {download_dir}')

    # create download_dir if needed
    download_dir.mkdir(parents=True, exist_ok=True)


    # get creodias user and passwd
    logger.debug('Loading environment variables from .env file')
    load_dotenv()

    try:
        os.environ["CREO_USER"]
    except:
        logger.error("The environment variable 'CREO_USER' is not set.")
        raise KeyError("The environment variable 'CREO_USER' is not set.")
    
    try:
        os.environ["CREO_PASSWORD"]
    except:
        logger.error("The environment variable 'CREO_PASSWORD' is not set.")
        raise KeyError("The environment variable 'CREO_PASSWORD' is not set.")



    # initialize dictionary for download urls
    S_dict = {}

# -------------------------------------------------------------------------- #

    # loop over all IDs in product list
    for ID in product_list:

        # check if product was already downloaded
        if (download_dir / f"{ID}.zip").is_file() or (download_dir / f"{ID}.SAFE").is_dir():
            if not overwrite:
                logger.info(f'Product {ID}.zip already exists. Not downloading again.')
                continue
            else:
                logger.info(f'Product {ID}.zip already exists. Overwriting existing file.')

        # search Creodias to find Sentinel products from list
        if ID.startswith('S1'):
            creo_search_url = f'https://finder.creodias.eu/resto/api/collections/Sentinel1/search.json?maxRecords=10&productIdentifier=%25{ID}.SAFE%25&sortParam=startDate&sortOrder=descending&status=all&dataset=ESA-DATASET'
            creo_search_results = ssdh.find_products(creo_search_url)
            # extract corresponding creodias uid
            uid = creo_search_results.json()['features'][0]['id']
            # add uid-identifier as key-value pair to dictionary
            S_dict[uid] = ID

    if S_dict:
        paths = ssdh.download_list(S_dict, os.environ["CREO_USER"], os.environ["CREO_PASSWORD"], download_dir)
        logger.info('Batch download finished! See you next time:)')

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# ---- End of <sentinel_download.py> ----

