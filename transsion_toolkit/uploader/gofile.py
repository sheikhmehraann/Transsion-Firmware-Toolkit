import os
import requests
import json
from transsion_toolkit.core.logger import logger
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

def get_gofile_server():
    """Fetch best available Gofile upload server."""
    try:
        resp = requests.get("https://api.gofile.io/servers", timeout=10)
        data = resp.json()
        if data.get("status") == "ok":
            servers = data.get("data", {}).get("servers", [])
            if servers:
                return servers[0]["name"]
    except Exception as e:
        logger.warning(f"[-] Error fetching Gofile servers: {e}")

    try:
        resp = requests.get("https://api.gofile.io/getBestServer", timeout=10)
        data = resp.json()
        if data.get("status") == "ok":
            return data.get("data", {}).get("server")
    except Exception:
        pass

    return "store1"

def create_session():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def upload_to_gofile(filepath, token=None):
    """
    Uploads a file to Gofile and returns the download page URL.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    server = get_gofile_server()
    upload_url = f"https://{server}.gofile.io/contents/uploadfile"
    filename = os.path.basename(filepath)
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)

    logger.info(f"[*] Uploading [bold cyan]{filename}[/bold cyan] ({file_size_mb:.2f} MB) to Gofile server: [bold green]{server}[/bold green]...")

    data = {}
    if token:
        data["token"] = token

    session = create_session()
    with open(filepath, "rb") as f:
        files = {"file": (filename, f)}
        resp = session.post(upload_url, data=data, files=files, timeout=600)

    res_json = resp.json()
    if res_json.get("status") == "ok":
        download_page = res_json.get("data", {}).get("downloadPage")
        logger.info("[bold green]=======================================================[/bold green]")
        logger.info(f"[bold green][✓] SUCCESS! File Uploaded to Gofile[/bold green]")
        logger.info(f"    Download Link: [bold cyan]{download_page}[/bold cyan]")
        logger.info("[bold green]=======================================================[/bold green]")
        return download_page
    else:
        raise RuntimeError(f"Gofile upload failed: {res_json}")
