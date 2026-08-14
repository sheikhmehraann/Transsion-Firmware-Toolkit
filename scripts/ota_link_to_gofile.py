#!/usr/bin/env python3
"""
Direct 4-Step Pipeline:
1. Input: OTA Link (Incremental or Full)
2. Download & Extract payload.bin to get .img files
3. Pack into Rama's format: X6871-...-images.tar.zst (zstd -19)
4. Upload directly to Gofile and return shareable link!
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

def download_file(url, dest_path):
    logger.info(f"[*] [1/4] Downloading OTA update package from:\n    {url}")
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    with session.get(url, headers=headers, stream=True, timeout=600) as r:
        r.raise_for_status()
        total_size = int(r.headers.get("content-length", 0))
        downloaded = 0
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=2 * 1024 * 1024): # 2MB chunks
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        pct = (downloaded / total_size) * 100
                        print(f"\r[*] Download Progress: {downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB ({pct:.1f}%)", end="", flush=True)
    print()
    logger.info(f"[bold green][✓] Download Complete: {dest_path}[/bold green]")
    return dest_path

def process_ota_link(ota_url, archive_name="X6871-15.1.2.180SP05-OP001PF001AZ-images.tar.zst", gofile_token=None, keep_files=False):
    work_dir = "temp_ota_extract_pipeline"
    extracted_dir = os.path.join(work_dir, "extracted_images")
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(extracted_dir, exist_ok=True)

    zip_file_path = os.path.join(work_dir, "ota_package.zip")

    try:
        # Step 1: Download OTA
        download_file(ota_url, zip_file_path)

        # Step 2: Extract payload.bin into raw .img files
        logger.info(f"[*] [2/4] Extracting payload.bin to partition images...")
        dumper = PayloadDumper(output_dir=extracted_dir)
        dumper.extract_from_zip(zip_file_path)

        # Step 3: Pack into Rama's .tar.zst format
        output_zst_path = os.path.join(work_dir, archive_name)
        logger.info(f"[*] [3/4] Packing partition images into {archive_name} via Zstandard level 19...")
        packager = ZstdPackager(compression_level=19)
        packager.pack_images(extracted_dir, output_zst_path)

        # Step 4: Upload to Gofile
        logger.info(f"[*] [4/4] Uploading {archive_name} to Gofile...")
        gofile_url = upload_to_gofile(output_zst_path, token=gofile_token)

        logger.info("\n" + "=" * 60)
        logger.info(f"[bold green][✓] SUCCESS! FULL PIPELINE COMPLETE[/bold green]")
        logger.info(f"    File:         {archive_name}")
        logger.info(f"    Gofile Link:  [bold cyan]{gofile_url}[/bold cyan]")
        logger.info("=" * 60 + "\n")

        return gofile_url

    finally:
        if not keep_files:
            logger.info("[*] Cleaning up temporary files...")
            shutil.rmtree(work_dir, ignore_errors=True)

def main():
    parser = argparse.ArgumentParser(description="Download OTA Link -> Extract payload.bin -> Pack .tar.zst -> Upload to Gofile")
    parser.add_argument("--url", required=True, help="Direct OTA URL (Incremental or Full)")
    parser.add_argument("--name", default="X6871-15.1.2.180SP05-OP001PF001AZ-images.tar.zst", help="Output archive name")
    parser.add_argument("--token", help="Optional Gofile token")
    parser.add_argument("--keep", action="store_true", help="Keep extracted files locally")
    args = parser.parse_args()

    process_ota_link(args.url, args.name, args.token, args.keep)

if __name__ == "__main__":
    main()
