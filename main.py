#!/usr/bin/env python3
"""
Transsion Firmware Toolkit - Main CLI Entry Point
The Ultimate All-in-One Firmware & OTA Toolkit for Transsion & MediaTek Devices.
Dedicated to and honoring the work of Rama Bondan Prakoso (@ramabondanp / rama982).
"""

import sys
import os
import argparse

# Reconfigure stdout for utf-8 if supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add local path to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transsion_toolkit.core.logger import logger
from transsion_toolkit.core.devices import TRANSSION_DEVICES
from transsion_toolkit.prober.google_checkin import GoogleCheckinProber
from transsion_toolkit.extractor.payload_dumper import PayloadDumper
from transsion_toolkit.extractor.zstd_packager import ZstdPackager
from transsion_toolkit.flasher.flasher import TranssionFastbootFlasher
from transsion_toolkit.uploader.gofile import upload_to_gofile

BANNER = """
=====================================================================
                    TRANSSION FIRMWARE TOOLKIT                       
      The Ultimate Firmware & OTA Suite for Infinix / TECNO / itel   
          (Honoring Rama Bondan Prakoso @ramabondanp / rama982)      
=====================================================================
"""

def main():
    parser = argparse.ArgumentParser(
        description="All-in-One Firmware & OTA Toolkit for Transsion (Infinix, TECNO, itel) & MediaTek Devices",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: ota-to-gofile (The Exact 4-Step Pipeline: URL -> Download -> Extract payload -> Pack .tar.zst -> Upload to Gofile)
    ota_gofile_parser = subparsers.add_parser("ota-to-gofile", help="Download OTA URL -> Extract payload.bin -> Pack Rama-style .tar.zst -> Upload to Gofile")
    ota_gofile_parser.add_argument("url", help="Direct OTA Update ZIP URL")
    ota_gofile_parser.add_argument("-n", "--name", default="X6871-15.1.2.180SP05-OP001PF001AZ-images.tar.zst", help="Custom output archive filename")
    ota_gofile_parser.add_argument("-t", "--token", help="Gofile account API token (optional)")
    ota_gofile_parser.add_argument("--keep", action="store_true", help="Keep local extracted files")

    # Command: probe-live
    live_parser = subparsers.add_parser("probe-live", help="Query official Google OTA servers live for real Full Tcard update URLs")
    live_parser.add_argument("-m", "--model", required=True, help="Device Codename or Config (e.g. X6871, KJ7, X6836, AD10)")

    # Command: upload-gofile
    up_parser = subparsers.add_parser("upload-gofile", help="Upload any local file or .tar.zst to Gofile")
    up_parser.add_argument("file", help="Path to file to upload")
    up_parser.add_argument("-t", "--token", help="Gofile user API token (optional)")

    # Command: extract
    extract_parser = subparsers.add_parser("extract", help="Extract raw partition images from a Full OTA zip or payload.bin")
    extract_parser.add_argument("input", help="Path to OTA .zip package or payload.bin")
    extract_parser.add_argument("-o", "--output", default="extracted_images", help="Output directory for images")

    # Command: pack
    pack_parser = subparsers.add_parser("pack", help="Compress extracted partition images into a high-ratio .tar.zst archive (Rama format)")
    pack_parser.add_argument("images_dir", help="Directory containing .img partition files")
    pack_parser.add_argument("-o", "--output", required=True, help="Output archive path (e.g. X6871-15.1.2.180SP05-images.tar.zst)")
    pack_parser.add_argument("-l", "--level", type=int, default=19, help="Zstandard compression level (1-22, default 19)")

    # Command: unpack
    unpack_parser = subparsers.add_parser("unpack", help="Decompress a .tar.zst archive into raw .img files")
    unpack_parser.add_argument("archive", help="Path to .tar.zst file")
    unpack_parser.add_argument("-o", "--output", default="unpacked_images", help="Output directory")

    # Command: flash
    flash_parser = subparsers.add_parser("flash", help="Automated Fastboot and Fastbootd multi-partition flasher")
    flash_parser.add_argument("images_dir", help="Directory containing extracted .img partition files")

    # Command: devices
    subparsers.add_parser("devices", help="List all cataloged Transsion device profiles and chipsets")

    args = parser.parse_args()

    print(BANNER)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "devices":
        logger.info("[bold cyan]=== Cataloged Transsion & MediaTek Devices ===[/bold cyan]")
        for codename, data in TRANSSION_DEVICES.items():
            logger.info(f"[bold green]{codename:8}[/bold green] | {data['brand']:7} | {data['market_name']:25} | {data['chipset']}")
        return

    if args.command == "ota-to-gofile":
        from scripts.ota_link_to_gofile import process_ota_link
        process_ota_link(args.url, args.name, args.token, args.keep)

    elif args.command == "probe-live":
        prober = GoogleCheckinProber(args.model)
        results = prober.probe_all_variants()
        if not results:
            logger.info("No updates currently found.")

    elif args.command == "upload-gofile":
        upload_to_gofile(args.file, args.token)

    elif args.command == "extract":
        dumper = PayloadDumper(args.output)
        if args.input.endswith(".zip"):
            dumper.extract_from_zip(args.input)
        else:
            dumper.extract_payload(args.input)

    elif args.command == "pack":
        packager = ZstdPackager(compression_level=args.level)
        packager.pack_images(args.images_dir, args.output)

    elif args.command == "unpack":
        packager = ZstdPackager()
        packager.unpack_archive(args.archive, args.output)

    elif args.command == "flash":
        flasher = TranssionFastbootFlasher(args.images_dir)
        flasher.check_fastboot_device()
        flasher.flash_boot_partitions()
        flasher.flash_super_partitions()
        flasher.reboot_system()

if __name__ == "__main__":
    main()
