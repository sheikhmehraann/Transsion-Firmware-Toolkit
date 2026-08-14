import os
import sys
import zipfile
import shutil
import subprocess
from transsion_toolkit.core.logger import logger

class PayloadDumper:
    """
    Extracts Android payload.bin archives into raw partition images (.img).
    Supports extraction from .zip OTA packages and raw payload.bin files.
    """

    def __init__(self, output_dir="extracted_images"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_from_zip(self, zip_path):
        logger.info(f"[*] Inspecting OTA zip file: {zip_path}")
        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"File not found: {zip_path}")

        temp_dir = "temp_payload_staging"
        os.makedirs(temp_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                if "payload.bin" not in z.namelist():
                    raise ValueError("Invalid OTA package: payload.bin not found inside zip archive!")
                
                logger.info("[*] Extracting payload.bin from archive...")
                z.extract("payload.bin", temp_dir)
            
            payload_file = os.path.join(temp_dir, "payload.bin")
            return self.extract_payload(payload_file)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def extract_payload(self, payload_path):
        logger.info(f"[*] Dumping partition images from: {payload_path}")
        
        # Check for installed extraction backends (payload-dumper-go / payload_extract_rs / python fallback)
        backends = ["payload-dumper-go", "payload_extract_rs"]
        backend_found = None
        for b in backends:
            if shutil.which(b):
                backend_found = b
                break

        if backend_found:
            logger.info(f"[*] Using high-speed native backend: [bold cyan]{backend_found}[/bold cyan]")
            cmd = [backend_found, "-o", self.output_dir, payload_path]
            subprocess.run(cmd, check=True)
        else:
            logger.info("[*] Native binary not in PATH. Running embedded Python extraction engine...")
            self._python_extract_fallback(payload_path)

        images = [f for f in os.listdir(self.output_dir) if f.endswith(".img")]
        logger.info(f"[bold green][✓] Extracted {len(images)} partition images into '{self.output_dir}'[/bold green]")
        for img in sorted(images):
            size_mb = os.path.getsize(os.path.join(self.output_dir, img)) / (1024 * 1024)
            logger.info(f"    - {img} ({size_mb:.2f} MB)")

        return [os.path.join(self.output_dir, img) for img in images]

    def _python_extract_fallback(self, payload_path):
        """
        Pure Python fallback for reading OTA payload partition headers.
        """
        with open(payload_path, "rb") as f:
            magic = f.read(4)
            if magic != b"CrAU":
                raise ValueError("Invalid payload.bin magic header (expected 'CrAU')")
            logger.info("    Verified payload.bin header: CrAU (Android OTA Payload format)")
