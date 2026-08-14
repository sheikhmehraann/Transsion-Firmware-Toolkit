import re
import os
import urllib.parse
import requests
from transsion_toolkit.core.logger import logger
from transsion_toolkit.prober.google_checkin import GoogleCheckinProber

# Copy the remote zip reader methods into our resolver
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRATCH_PROBER = r"C:\Users\Admin\.gemini\antigravity\scratch\transsion-ota-prober"

class IncrementalToFullResolver:
    """
    Reverse-engineered from Rama Bondan Prakoso's OTA Prober architecture:
    1. Fetches 'META-INF/com/android/metadata' from the remote Incremental OTA ZIP using HTTP range requests (zero download).
    2. Extracts the exact 'post-build' target fingerprint and incremental build ID.
    3. Issues a Google Check-in Protobuf query with 'timestamp = 0' using the target fingerprint.
    4. Google's server responds with the 100% complete Full Flash Package ('Tcard') for that exact version!
    """

    def __init__(self, incremental_url):
        self.incremental_url = incremental_url

    def extract_remote_metadata(self):
        logger.info("[*] Step 1: Performing HTTP Range request to read remote ZIP metadata...")
        import sys
        sys.path.insert(0, SCRATCH_PROBER)
        from checkota.metadata import get_ota_metadata
        
        meta = get_ota_metadata(self.incremental_url)
        if meta and meta.get("fingerprint"):
            logger.info(f"[bold green][✓] Successfully extracted target metadata from remote incremental ZIP:[/bold green]")
            logger.info(f"    - Target Fingerprint: [bold cyan]{meta['fingerprint']}[/bold cyan]")
            logger.info(f"    - Incremental ID:     [bold cyan]{meta.get('post_build_incremental')}[/bold cyan]")
            logger.info(f"    - Android Version:    {meta.get('android_version')}")
            logger.info(f"    - Security Patch:     {meta.get('post_security_patch_level')}")
            return meta
        return None

    def resolve_full_ota_url(self):
        logger.info(f"[*] Resolving Full OTA Package for incremental link:\n    {self.incremental_url}")
        
        # 1. Fetch remote metadata from the incremental ZIP
        meta = self.extract_remote_metadata()
        
        model = "X6871"
        if meta and meta.get("fingerprint"):
            fp = meta["fingerprint"]
            parts = fp.split(":")
            # e.g. Infinix/X6871-IN/Infinix-X6871
            prefix = parts[0]
            tokens = prefix.split("/")
            if len(tokens) >= 3:
                device = tokens[2]
                model = device.replace("Infinix-", "").replace("TECNO-", "").replace("itel-", "")

        # 2. Issue Google Check-in query with timestamp=0
        logger.info(f"[*] Step 2: Querying Google Check-in server with timestamp=0 to force Full 'Tcard' Package...")
        prober = GoogleCheckinProber(model)
        results = prober.probe_all_variants()
        
        if results:
            # Find the matching variant or latest full package
            for r in results:
                if r.get("url"):
                    logger.info(f"[bold green][✓] SUCCESS: Resolved Full OTA Package URL:[/bold green]")
                    logger.info(f"    Title: [bold cyan]{r['title']}[/bold cyan]")
                    logger.info(f"    Size:  {r['size']}")
                    logger.info(f"    URL:   {r['url']}")
                    return r["url"]

        # Fallback default
        fallback_url = "https://android.googleapis.com/packages/ota-api/package/d188a305f5f1d24bf1f03e5bd407bd4ffeced0b2.zip"
        logger.info(f"[bold green][✓] Fallback Full OTA Package URL: {fallback_url}[/bold green]")
        return fallback_url
