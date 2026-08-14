#!/usr/bin/env python3
"""
Automated Pipeline: Incremental/Full OTA Link -> Auto-Resolve Full OTA -> Extract All .img Partitions -> Pack Rama-style .tar.zst -> Upload to Gofile
NO BASE FIRMWARE NEEDED!
"""

import os
import sys
import argparse
import requests
import zipfile
import shutil
import re
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transsion_toolkit.core.logger import logger
from transsion_toolkit.extractor.payload_dumper import PayloadDumper
from transsion_toolkit.extractor.zstd_packager import ZstdPackager
from transsion_toolkit.uploader.gofile import upload_to_gofile
from transsion_toolkit.prober.incremental_to_full import IncrementalToFullResolver

def download_file(url, dest_path):
    logger.info(f"[*] Downloading OTA package from:\n    {url}")
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    with session.get(url, headers=headers, stream=True, timeout=600) as r:
        r.raise_for_status()
        total_size = int(r.headers.get("content-length", 0))
        downloaded = 0
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024): # 1MB chunks
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        pct = (downloaded / total_size) * 100
                        print(f"\r[*] Downloading: {downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB ({pct:.1f}%)", end="", flush=True)
    print()
    logger.info(f"[bold green][✓] Download Complete: {dest_path}[/bold green]")
    return dest_path

def guess_archive_name(url, model=None, version=None):
    if model and version:
        return f"{model}-{version}-images.tar.zst"
    parsed = urlparse(url)
    basename = os.path.basename(parsed.path)
    match = re.search(r"([A-Za-z0-9]+[-_][0-9A-Za-z\.\-_]+)", basename)
    if match:
        name = match.group(1).replace(".zip", "")
        return f"{name}-images.tar.zst"
    return "X6871-15.1.2.180SP05-OP001PF001AZ-images.tar.zst"

def process_ota_to_gofile(ota_url, output_name=None, gofile_token=None, is_incremental=False, keep_files=False):
    work_dir = "temp_ota_pipeline"
    extracted_dir = os.path.join(work_dir, "extracted_images")
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(extracted_dir, exist_ok=True)

    target_download_url = ota_url
    model = "X6871"
    target_version = "15.1.2.180SP05"

    # If it's an incremental link or contains incremental keywords
    if is_incremental or any(k in ota_url.lower() for k in ["inc", "incremental", "diff", "to"]):
        logger.info("[bold yellow][*] Incremental OTA Link Detected![/bold yellow]")
        logger.info("[*] Converting Incremental OTA link -> FULL OTA Link (No base image needed)...")
        resolver = IncrementalToFullResolver(ota_url)
        model, target_version = resolver.parse_metadata_from_url()
        target_download_url = resolver.resolve_full_ota_url()

    ota_zip_path = os.path.join(work_dir, "ota_update.zip")

    try:
        # Step 1: Download Full OTA
        download_file(target_download_url, ota_zip_path)

        # Step 2: Extract payload.bin and dump all .img files
        dumper = PayloadDumper(output_dir=extracted_dir)
        dumper.extract_from_zip(ota_zip_path)

        # Step 3: Pack into Rama-format .tar.zst
        if not output_name:
            output_name = guess_archive_name(target_download_url, model, target_version)

        archive_path = os.path.join(work_dir, output_name)
        packager = ZstdPackager(compression_level=19)
        packager.pack_images(extracted_dir, archive_path)

        # Step 4: Upload to Gofile
        gofile_url = upload_to_gofile(archive_path, token=gofile_token)

        logger.info(f"[bold green]=======================================================[/bold green]")
        logger.info(f"[bold green][★] ALL DONE! Direct Flashable .tar.zst on Gofile:[/bold green]")
        logger.info(f"    Gofile Download Link: [bold cyan]{gofile_url}[/bold cyan]")
        logger.info(f"    Archive Name:         {output_name}")
        logger.info(f"[bold green]=======================================================[/bold green]")
        return gofile_url

    finally:
        if not keep_files:
            logger.info("[*] Cleaning up temporary working files...")
            shutil.rmtree(work_dir, ignore_errors=True)

def main():
    parser = argparse.ArgumentParser(description="Convert Incremental/Full OTA Link -> Extract All Partitions -> Pack .tar.zst -> Upload to Gofile (No base needed)")
    parser.add_argument("--url", required=True, help="OTA update link (incremental or full)")
    parser.add_argument("--name", help="Custom output archive filename (e.g. X6871-15.1.2.180SP05-OP001PF001AZ-images.tar.zst)")
    parser.add_argument("--incremental", action="store_true", help="Explicitly mark link as incremental to force Full OTA resolution")
    parser.add_argument("--token", help="Gofile account API token (optional)")
    parser.add_argument("--keep", action="store_true", help="Keep local extracted files")
    args = parser.parse_args()

    process_ota_to_gofile(args.url, args.name, args.token, args.incremental, args.keep)

if __name__ == "__main__":
    main()
