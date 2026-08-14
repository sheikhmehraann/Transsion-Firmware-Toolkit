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
from transsion_toolkit.prober.ota_prober import TranssionOTAProber
from transsion_toolkit.prober.incremental_to_full import IncrementalToFullResolver
from transsion_toolkit.extractor.payload_dumper import PayloadDumper
from transsion_toolkit.extractor.incremental_reconstructor import IncrementalReconstructor
from transsion_toolkit.extractor.zstd_packager import ZstdPackager
from transsion_toolkit.flasher.flasher import TranssionFastbootFlasher
from transsion_toolkit.vendor_fix.vendor64_converter import Vendor64Converter
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

    # Command: probe-live (Direct Google Check-in API using Rama's config database)
    live_parser = subparsers.add_parser("probe-live", help="Query official Google OTA servers live for real Full Tcard update URLs (Rama method)")
    live_parser.add_argument("-m", "--model", required=True, help="Device Codename or Config (e.g. X6871, KJ7, X6836, AD10)")

    # Command: ota-to-gofile (Handles both Incremental and Full links seamlessly without base images)
    ota_gofile_parser = subparsers.add_parser("ota-to-gofile", help="Direct OTA URL (Incremental or Full) -> Dump All .img Files -> Pack Rama-style .tar.zst -> Upload to Gofile")
    ota_gofile_parser.add_argument("url", help="Direct OTA Update ZIP URL")
    ota_gofile_parser.add_argument("-n", "--name", help="Custom output archive filename (e.g. X6871-15.1.2.180SP05-OP001PF001AZ-images.tar.zst)")
    ota_gofile_parser.add_argument("-i", "--incremental", action="store_true", help="Force incremental-to-full resolution")
    ota_gofile_parser.add_argument("-t", "--token", help="Gofile account API token (optional)")
    ota_gofile_parser.add_argument("--keep", action="store_true", help="Keep local extracted files")

    # Command: full-ota-to-gofile (Queries live Full OTA package for model, extracts all images, packs .tar.zst, and uploads to Gofile)
    auto_parser = subparsers.add_parser("auto-ota", help="1-Click: Query live Full OTA from Google -> Dump .img -> Pack .tar.zst -> Upload to Gofile")
    auto_parser.add_argument("-m", "--model", required=True, help="Device Model (e.g. X6871)")
    auto_parser.add_argument("-t", "--token", help="Gofile account API token (optional)")

    # Command: inc-to-full (Resolve an Incremental OTA URL to its corresponding Full OTA URL)
    inc_parser = subparsers.add_parser("inc-to-full", help="Resolve an Incremental OTA URL to its corresponding Full OTA URL")
    inc_parser.add_argument("url", help="Incremental OTA URL")

    # Command: upload-gofile
    up_parser = subparsers.add_parser("upload-gofile", help="Upload any local file or .tar.zst to Gofile")
    up_parser.add_argument("file", help="Path to file to upload")
    up_parser.add_argument("-t", "--token", help="Gofile user API token (optional)")

    # Command: extract
    extract_parser = subparsers.add_parser("extract", help="Extract raw partition images from a Full OTA zip or payload.bin")
    extract_parser.add_argument("input", help="Path to OTA .zip package or payload.bin")
    extract_parser.add_argument("-o", "--output", default="extracted_images", help="Output directory for images")

    # Command: reconstruct
    recon_parser = subparsers.add_parser("reconstruct", help="Reconstruct new partition images from an Incremental OTA using old source images")
    recon_parser.add_argument("payload", help="Path to incremental payload.bin")
    recon_parser.add_argument("-s", "--source", required=True, help="Directory containing base source .img files from old version")
    recon_parser.add_argument("-o", "--output", default="target_images", help="Output directory for updated images")

    # Command: pack (Create .tar.zst)
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

    # Command: fix-vendor
    fix_parser = subparsers.add_parser("fix-vendor", help="Convert hybrid 32/64-bit Transsion vendor tree to pure 64-bit only for GSIs")
    fix_parser.add_argument("vendor_dir", help="Directory of unpacked vendor partition")

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

    if args.command == "probe-live":
        prober = GoogleCheckinProber(args.model)
        results = prober.probe_all_variants()
        if not results:
            logger.info("No updates currently found.")

    elif args.command == "auto-ota":
        from scripts.ota_link_to_gofile import process_ota_to_gofile
        prober = GoogleCheckinProber(args.model)
        results = prober.probe_all_variants()
        if results:
            first_res = results[0]
            url = first_res["url"]
            title = first_res["title"] or f"{args.model}-latest"
            archive_name = f"{title.replace('Tcard_', '')}-images.tar.zst"
            logger.info(f"[*] Triggering Automated Pipeline for Live Full OTA: {url}")
            process_ota_to_gofile(url, output_name=archive_name, gofile_token=args.token)
        else:
            logger.error(f"[-] No live Full OTA found for model: {args.model}")

    elif args.command == "inc-to-full":
        resolver = IncrementalToFullResolver(args.url)
        full_url = resolver.resolve_full_ota_url()
        print(f"\n[+] Resolved Full OTA Link: {full_url}")

    elif args.command == "ota-to-gofile":
        from scripts.ota_link_to_gofile import process_ota_to_gofile
        process_ota_to_gofile(args.url, args.name, args.token, args.incremental, args.keep)

    elif args.command == "upload-gofile":
        upload_to_gofile(args.file, args.token)

    elif args.command == "extract":
        dumper = PayloadDumper(args.output)
        if args.input.endswith(".zip"):
            dumper.extract_from_zip(args.input)
        else:
            dumper.extract_payload(args.input)

    elif args.command == "reconstruct":
        recon = IncrementalReconstructor(args.source, args.output)
        recon.reconstruct(args.payload)

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

    elif args.command == "fix-vendor":
        converter = Vendor64Converter(args.vendor_dir)
        converter.convert_vendor()

if __name__ == "__main__":
    main()
