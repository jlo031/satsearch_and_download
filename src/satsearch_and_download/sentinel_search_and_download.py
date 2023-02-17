# ---- This is <sentinel_search_and_download.py> ----

"""
Module to facilitate search and batch download of Copernicus Sentinel data.
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

def sentinel_search(
    sensors, 
    area, 
    starttime, 
    endtime,
    area_relation='Intersects',
    cloudcover='0,30',
    search_dir=pathlib.Path.cwd() / 'search_results',
    overwrite=False,
    loglevel = 'INFO'
):
    
    """Search for Sentinel products

    Parameters
    ----------
    sensors:
        list of Sentinel sensors to be included in the search (choices = ['S1', 'S2', 'S3'])
    area:
        path to geojson file defining the area of interest (polygon)
    starttime:
        sensing start time 'YYYY-MM-DD HH:MM'
    endtime:
        sensing end time 'YYYY-MM-DD HH:MM'
    area_relation:
        aree relation of polygon and products (choices = ['Contains', 'Intersects']
    cloudcover:
        cloud cover percentage 'min,max' (default = '0,30')
    search_dir:
        path to directory where search results are saved in .geojson and .txt files. By default, folder 'search_results' will be created in the current work directory.
    overwrite:
        overwrite existing search results (default=False)
    loglevel:
        set logger level (default=INFO)
    """
    
    # remove default logger handler and add personal one
    logger.remove()
    logger.add(sys.stderr, level=loglevel)


    # convert folder strings to paths
    json_path         = pathlib.Path(area).expanduser().absolute()
    search_result_dir = pathlib.Path(search_dir).expanduser().absolute()

    logger.debug(f'json_path:         {json_path}')
    logger.debug(f'search_result_dir: {search_result_dir}')

    # convert cloudcover and time stamps to required format
    starttime = parse(starttime, settings={"DATE_ORDER": "YMD"})
    endtime   = parse(endtime, settings={"DATE_ORDER": "YMD"})
    cloudcover = (int(cloudcover.split(",")[0]), int(cloudcover.split(",")[1]))

    logger.debug(f'starttime:  {starttime}')
    logger.debug(f'endtime:    {endtime}')
    logger.debug(f'cloudcover: {cloudcover}')
    
    if not json_path.is_file() and (json_path.suffix == '.geojson'):
        logger.error(f"json_path {json_path} is not a '.geojson' file")
        raise FileNotFoundError(f"json_path {json_path} is not a '.geojson' file")


    # create search_result_dir if needed
    search_result_dir.mkdir(parents=True, exist_ok=True)

    # build path to search result txt file
    search_result_path = search_result_dir / f'search_result_{json_path.stem}_{starttime.isoformat()}_{endtime.isoformat()}.txt'

    logger.debug(f'search_result_path: {search_result_path}')

# -------------------------------------------------------------------------- #

    # get scihub user and passwd
    logger.debug('Loading environment variables from .env file')
    load_dotenv()

    try:
        os.environ["DHUS_USER"]
    except:
        logger.error("The environment variable 'DHUS_USER' is not set.")
        raise KeyError("The environment variable 'DHUS_USER' is not set.")
    
    try:
        os.environ["DHUS_PASSWORD"]
    except:
        logger.error("The environment variable 'DHUS_PASSWORD' is not set.")
        raise KeyError("The environment variable 'DHUS_PASSWORD' is not set")


    # create sentinelAPI
    try:
        s_api = SentinelAPI(os.environ["DHUS_USER"], os.environ["DHUS_PASSWORD"])
    except KeyError:
        logger
        raise KeyError("Cannot login to Copernicus SciHub, check if username (DHUS_USER) and password (DHUS_PASSWORD) are set correctly in .env file")

# -------------------------------------------------------------------------- #

    # Sentinel-1
    if 'S1' in sensors:
        logger.info("Searching for Sentinel-1 GRD products")
        S1products = s_api.query(
            area = geojson_to_wkt(read_geojson(json_path)),
            date = (starttime, endtime),
            area_relation = area_relation,
            platformname = "Sentinel-1",
            producttype = "GRD",
        )
            
        # count how many products were found
        n_products = s_api.count(
            area = geojson_to_wkt(read_geojson(json_path)),
            date = (starttime, endtime),
            area_relation = area_relation,
            platformname = "Sentinel-1",
            producttype = "GRD",
            )

        logger.info(f'Found {n_products} S1 products')
        logger.info(f'Found {str(len(S1products))} S1 products')      

# -------------------------------------------------------------------------- #

    # Sentinel-2
    if "S2" in sensors:
        logger.info(f"Searching for Sentinel-2 products with cloudcover {str(cloudcover)}")
        S2products = s_api.query(
            area = geojson_to_wkt(read_geojson(area)),
            date = (starttime, endtime),
            area_relation = area_relation,
            platformname = "Sentinel-2",
            processinglevel = "Level-1C",
            cloudcoverpercentage = cloudcover,
         )

        # count how many products were found
        n_products = s_api.count(
            area = geojson_to_wkt(read_geojson(area)),
            date = (starttime, endtime),
            area_relation = area_relation,
            platformname = "Sentinel-2",
            processinglevel = "Level-1C",
            cloudcoverpercentage = cloudcover,
        )

        logger.info(f'Found {n_products} S2 products')
        logger.info(f'Found {str(len(S2products))} S2 products')      

# -------------------------------------------------------------------------- #

    # Sentinel-3
    if "S3" in sensors:
        logger.info(f"Searching for Sentinel-3 OLCI products with cloudcover {str(cloudcover)}")
        # Temporary raising the logging level to avoid logging the results from both S3_2_LFRproducts and S3_1_EFRproducts
        logger.remove()
        logger.add(sys.stderr, level='WARNING')

        # Searching for level-2 products
        S3_2_LFRproducts = s_api.query(
            area = geojson_to_wkt(read_geojson(area)),
            date = (starttime, endtime),
            area_relation = area_relation,
            platformname = "Sentinel-3",
            instrumentshortname = "OLCI",
            producttype = "OL_2_LFR___",
            cloudcoverpercentage = cloudcover,
        )

        # Searching for level-1 products
        S3_1_EFRproducts = s_api.query(
            area = geojson_to_wkt(read_geojson(area)),
            date = (starttime, endtime),
            area_relation = area_relation,
            platformname = "Sentinel-3",
            instrumentshortname = "OLCI",
            producttype = "OL_1_EFR___",
        )

        # set loglevel back to original value
        logger.remove()
        logger.add(sys.stderr, level=loglevel)

        # Find the level-1 products corresponding to the level-2 products filtered with respect to cloud cover
        S3products = OrderedDict()
        for k in S3_2_LFRproducts.values():
            for j in S3_1_EFRproducts.values():
                if j["identifier"][16:47] == k["identifier"][16:47]:
                    if j["identifier"] not in S3products.values():
                        S3products[j["uuid"]] = j

        logger.info(f'Found {str(len(S3products))} S3 products')      

# -------------------------------------------------------------------------- #




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

# ---- End of <sentinel_search_and_download.py> ----

