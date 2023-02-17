# ---- This is <SLib.py> ----

"""
Library with functions for Sentinel search through SciHub and download through Creodias

C.Taelman
Dec 2022
"""

from pathlib import Path
import shutil
import requests
from loguru import logger

import concurrent.futures
from tqdm import tqdm
from keycloak import KeycloakOpenID
import keycloak


# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

def OpenID():
    """Identify on Creodias"""

    try:
        r = KeycloakOpenID(
            server_url="https://auth.creodias.eu/auth/",
            client_id="CLOUDFERRO_PUBLIC",
            realm_name="DIAS"
        )
    except keycloak.exceptions.KeycloakError:
        logger.warning('Timeout')
        OpenID()
    except keycloak.exceptions.KeycloakGetError:
        logger.warning('Timeout')
        OpenID()

    return r

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# TO DO: use request.POST(token_url) instead?? See Github repo

def get_token(username, password):
    """Request token from Creodias

    Parameters
    ----------
    username : Creodias username
    password : Creodias password
    """

    keycloak_openid = OpenID()
    logger.info("ID opened")

    return keycloak_openid.token(username, password)

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

def find_products(url: str):
    """Find products on Creodias via URL

    Parameters
    ----------
    url : Creodias Finder URL
    """

    try:
        results = requests.get(url)
    except requests.exceptions.Timeout:
        logger.warning('Timeout')
        results = find_products(url)
    except requests.exceptions.TooManyRedirects:
        return None
    except requests.exceptions.RequestException as e:
        raise SystemExit(e) from e

    return results

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

def download_raw_data(url, outfile, show_progress):
    """Downloads data from url to outfile.incomplete and then moves to outfile

    Parameters
    ----------
    url : CreoDIAS url for download
    outfile : Path where download is stored
    show_progress : if True, shows progress bar per download
    """

    outfile_temp = str(outfile) + ".incomplete"

    try:
        downloaded_bytes = 0
        logger.info('Downloading ...')
        with requests.get(url, stream=True, timeout=100) as req:
            with tqdm(unit="B", unit_scale=True, disable=not show_progress) as progress:
                chunk_size = 2 ** 20  # download in 1 MB chunks
                with open(outfile_temp, "wb") as fout:
                    for chunk in req.iter_content(chunk_size=chunk_size):
                        if chunk:  # filter out keep-alive new chunks
                            fout.write(chunk)
                            progress.update(len(chunk))
                            downloaded_bytes += len(chunk)
        shutil.move(outfile_temp, outfile)
    finally:
        try:
            Path(outfile_temp).unlink()
        except OSError:
            pass

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

def download(uid, username, password, outfile, show_progress=True):
    """Download a file from CreoDIAS by UID to outfile

    Parameters
    ----------
    uid : Creodias UID to download
    username : Creodias sername
    password : Creodias password
    outfile : Path where downloads are stored
    show_progress : if True, shows progress bar per download
    """

    token = get_token(username, password)
    download_url = "https://zipper.creodias.eu/download"
    url = f"{download_url}/{uid}?token={token['access_token']}"
    download_raw_data(url, outfile, show_progress)

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

def download_list(S_dict, username, password, outdir, threads=1, show_progress=True):
    """Downloads a list of images by their UID

    Parameters
    ----------
    S_dict : dictionary with UIDS as keys, Sentinel identifiers  as values!
    username : Creodias username
    password : Creodias password
    outdir :  Output directory for downloads
    threads : Number of simultaneous downloads

    Returns
    -------
    paths : dict mapping uids to paths of downloaded files
    """

    uids = list(S_dict.keys())
    
    if show_progress:
        pbar = tqdm(total=len(uids), unit="files")

    def download_uid(uid):
        outfile = Path(outdir) / f"{S_dict[uid]}.zip"
        download(uid, username, password, outfile=outfile, show_progress=False)
        if show_progress:
            pbar.update(1)
        return uid, outfile

    with concurrent.futures.ThreadPoolExecutor(threads) as executor:
        paths = dict(executor.map(download_uid, uids))

    return paths

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# ---- End of <SLib.py> ----
