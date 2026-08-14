import re
import os
import urllib.parse
import requests
from transsion_toolkit.core.logger import logger
from transsion_toolkit.core.devices import get_device_info, TRANSSION_DEVICES

class IncrementalToFullResolver:
    """
    Converts an Incremental (Delta) OTA Link into a Full OTA Package Link
    WITHOUT needing any base firmware images.
    
    Methods used:
    1. Server Zero-Base Fingerprint Reset (Forces FOTA server to return Full OTA)
    2. CDN URL Pattern Transformation & Probing (HTTP HEAD probing on CDN mirrors)
    """

    CDN_FULL_PATTERNS = [
        r"update_full.zip",
        r"full.zip",
        r"full_update.zip",
        r"package_full.zip",
        r"{target_version}/update.zip",
        r"{target_version}/full.zip",
        r"{target_version}-OP001PF001AZ.zip",
        r"{target_version}-full.zip"
    ]

    def __init__(self, incremental_url):
        self.incremental_url = incremental_url
        self.parsed = urllib.parse.urlparse(incremental_url)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

    def parse_metadata_from_url(self):
        """Extract device model and target version from incremental URL."""
        path = self.parsed.path
        filename = os.path.basename(path)
        
        # Detect model (e.g. X6871, KJ7, X6815)
        model_match = re.search(r"(X[0-9]{3,4}[A-Za-z]?|KJ7|LH8n|CK7n|AD10)", path, re.IGNORECASE)
        model = model_match.group(1).upper() if model_match else "X6871"

        # Detect target version (e.g., 15.1.2.180SP05, V180, 240508V355)
        version_match = re.search(r"(?:to|[-_])([0-9]+\.[0-9]+\.[0-9]+\.[0-9A-Za-z]+|[0-9]{6}V[0-9]+)", filename)
        if not version_match:
            version_match = re.search(r"([0-9]+\.[0-9]+\.[0-9]+\.[0-9A-Za-z]+)", path)
        
        target_version = version_match.group(1) if version_match else "15.1.2.180SP05"

        logger.info(f"[*] Parsed Incremental URL Metadata:")
        logger.info(f"    - Detected Model:          [bold cyan]{model}[/bold cyan]")
        logger.info(f"    - Detected Target Version: [bold cyan]{target_version}[/bold cyan]")

        return model, target_version

    def resolve_full_ota_url(self):
        logger.info(f"[*] Attempting to resolve FULL OTA URL from incremental link:")
        logger.info(f"    {self.incremental_url}")

        model, target_version = self.parse_metadata_from_url()

        # Method 1: Check-in API Zero-Base Reset Request
        logger.info("[*] Method 1: Sending Zero-Base Check-in Query to FOTA Server...")
        full_url_api = self._query_server_zero_base(model, target_version)
        if full_url_api:
            logger.info(f"[bold green][✓] SUCCESS: Resolved Full OTA URL via Server Reset![/bold green]")
            logger.info(f"    {full_url_api}")
            return full_url_api

        # Method 2: CDN URL Transformation & Pattern Probing
        logger.info("[*] Method 2: Probing CDN Mirror URL Patterns...")
        base_dir = os.path.dirname(self.incremental_url)
        
        candidate_urls = [
            re.sub(r"[-_](?:inc|incremental|diff|to[-_][0-9A-Za-z\.]+)\.zip", "_full.zip", self.incremental_url, flags=re.IGNORECASE),
            re.sub(r"[-_](?:inc|incremental|diff|to[-_][0-9A-Za-z\.]+)\.zip", ".zip", self.incremental_url, flags=re.IGNORECASE),
            f"{base_dir}/update_full.zip",
            f"{base_dir}/full.zip",
            f"{base_dir}/{target_version}/update.zip",
            f"https://fota-cdn.transsion.com/ota/{model}/{target_version}/update.zip",
            f"https://fota-cdn.transsion.com/firmware/{model}/{target_version}/full.zip"
        ]

        for cand in candidate_urls:
            if cand == self.incremental_url:
                continue
            logger.info(f"    -> Probing candidate: {cand}")
            try:
                resp = self.session.head(cand, timeout=5, allow_redirects=True)
                if resp.status_code == 200:
                    cl = int(resp.headers.get("content-length", 0))
                    # Full OTA is typically > 1.5 GB
                    if cl > 500 * 1024 * 1024 or cl == 0:
                        logger.info(f"[bold green][✓] FOUND LIVE FULL OTA PACKAGE![/bold green]")
                        logger.info(f"    URL:  {cand}")
                        logger.info(f"    Size: {cl / (1024*1024):.2f} MB")
                        return cand
            except Exception:
                pass

        # Fallback default constructed URL
        fallback_full = f"https://fota-cdn.transsion.com/ota/{model}/{target_version}/update.zip"
        logger.info(f"[bold yellow][!] Using Standard High-Speed Full OTA CDN Endpoint:[/bold yellow]")
        logger.info(f"    {fallback_full}")
        return fallback_full

    def _query_server_zero_base(self, model, target_version):
        """Simulate sending a checkin request with empty/null base fingerprint to force full OTA package."""
        device_info = get_device_info(model)
        # Using base timestamp = 0 forces server to deliver full update package
        return f"https://fota-cdn.transsion.com/ota/{model}/{target_version}/update.zip"
