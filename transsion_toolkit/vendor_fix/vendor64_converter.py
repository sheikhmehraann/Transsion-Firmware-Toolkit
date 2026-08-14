import os
import re
from transsion_toolkit.core.logger import logger

class Vendor64Converter:
    """
    Converts Transsion 32/64-bit hybrid vendor partitions and build.prop configurations
    into pure 64-bit only (arm64-v8a) to enable seamless GSI (Generic System Image) booting.
    Based upon Rama Bondan Prakoso's Transsion-vendor64_32-to-vendor64-only-fix.
    """

    def __init__(self, vendor_mount_dir):
        self.vendor_dir = vendor_mount_dir

    def convert_vendor(self):
        logger.info(f"[*] Starting 64-Bit Vendor Conversion on: [bold cyan]{self.vendor_dir}[/bold cyan]")
        
        prop_paths = [
            os.path.join(self.vendor_dir, "build.prop"),
            os.path.join(self.vendor_dir, "odm", "build.prop"),
            os.path.join(self.vendor_dir, "etc", "build.prop"),
            os.path.join(self.vendor_dir, "default.prop")
        ]

        modified_count = 0
        for prop in prop_paths:
            if os.path.isfile(prop):
                logger.info(f"[*] Patching property file: {prop}")
                if self._patch_prop_file(prop):
                    modified_count += 1

        logger.info(f"[bold green][✓] Successfully converted vendor properties across {modified_count} prop files![/bold green]")
        logger.info("    -> GSI 64-bit only architecture is now fully compatible.")

    def _patch_prop_file(self, filepath):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        original = content
        
        # Replace 32-bit cpu abilists
        content = re.sub(r"ro\.vendor\.product\.cpu\.abilist\s*=.*", "ro.vendor.product.cpu.abilist=arm64-v8a", content)
        content = re.sub(r"ro\.vendor\.product\.cpu\.abilist32\s*=.*", "ro.vendor.product.cpu.abilist32=", content)
        content = re.sub(r"ro\.odm\.product\.cpu\.abilist\s*=.*", "ro.odm.product.cpu.abilist=arm64-v8a", content)
        content = re.sub(r"ro\.odm\.product\.cpu\.abilist32\s*=.*", "ro.odm.product.cpu.abilist32=", content)
        content = re.sub(r"ro\.product\.cpu\.abilist32\s*=.*", "ro.product.cpu.abilist32=", content)

        if content != original:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info("    [✓] Stripped 32-bit abilist definitions.")
            return True
        return False
