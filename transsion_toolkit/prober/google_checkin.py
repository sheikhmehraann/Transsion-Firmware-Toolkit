import os
import sys
import datetime
import gzip
from pathlib import Path
import requests
import yaml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VENDOR_DIR = os.path.join(ROOT_DIR, "vendor", "google-ota-prober")
sys.path.insert(0, VENDOR_DIR)

from checkin import checkin_generator_pb2
from utils import functions
from transsion_toolkit.core.logger import logger

CHECKIN_URL = "https://android.clients.google.com/checkin"
PROTO_TYPE = "application/x-protobuffer"
USER_AGENT_TPL = "Android-Checkin/2.0 ({} {}; build {}); gzip"

class GoogleCheckinProber:
    """
    Direct Google Check-in Protobuf client for querying official Android Full/Incremental OTA packages.
    Based on the exact mechanism used by Rama Bondan Prakoso (@ramabondanp) in transsion-ota-prober.
    """

    def __init__(self, config_path_or_model):
        self.configs = []
        if os.path.isfile(config_path_or_model):
            self._load_from_yaml(config_path_or_model)
        else:
            # Look up config in configs/
            cfg_file = os.path.join(ROOT_DIR, "configs", f"config-{config_path_or_model.upper()}.yml")
            if not os.path.isfile(cfg_file):
                cfg_file = os.path.join(ROOT_DIR, "configs", f"config-{config_path_or_model}.yml")
            if os.path.isfile(cfg_file):
                self._load_from_yaml(cfg_file)
            else:
                raise FileNotFoundError(f"No configuration file found for device: {config_path_or_model}")

    def _load_from_yaml(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        variants = data.get("variants")
        base = {k: v for k, v in data.items() if k != "variants"}

        if variants:
            for v in variants:
                merged = {**base, **v}
                self.configs.append(merged)
        else:
            self.configs.append(base)

    def probe_all_variants(self):
        results = []
        for cfg in self.configs:
            res = self.probe_variant(cfg)
            if res:
                results.append(res)
        return results

    def probe_variant(self, cfg):
        oem = cfg.get("oem", "Infinix")
        product = cfg.get("product", "X6871-OP")
        device = cfg.get("device", "Infinix-X6871")
        android_version = str(cfg.get("android_version", "15"))
        build_tag = cfg.get("build_tag", "AP3A.240905.015.A2")
        incremental = str(cfg.get("incremental", "180003"))
        model = cfg.get("model", "Infinix GT 20 Pro")
        variant = cfg.get("variant", product)

        fingerprint = f"{oem}/{product}/{device}:{android_version}/{build_tag}/{incremental}:user/release-keys"

        logger.info(f"[*] Querying Official Google OTA Server for: [bold cyan]{model}[/bold cyan] ({variant})")
        logger.info(f"    Fingerprint: {fingerprint}")

        imei = functions.generateImei()
        digest = functions.generateDigest()
        serial = functions.generateSerial()
        mac = functions.generateMac()
        ua = USER_AGENT_TPL.format(android_version, model, build_tag)

        payload = checkin_generator_pb2.AndroidCheckinRequest()
        build = checkin_generator_pb2.AndroidBuildProto()
        checkin = checkin_generator_pb2.AndroidCheckinProto()

        build.id = fingerprint
        build.timestamp = 0  # CRUCIAL: Setting timestamp=0 instructs server that device has no base, FORCING Full Tcard Package!
        build.device = device

        checkin.build.CopyFrom(build)
        checkin.roaming = "WIFI::"
        checkin.userNumber = 0
        checkin.deviceType = 2
        checkin.voiceCapable = False

        payload.imei = imei
        payload.id = 0
        payload.digest = digest
        payload.checkin.CopyFrom(checkin)
        payload.locale = "en-US"
        payload.timeZone = "America/New_York"
        payload.version = 3
        payload.serialNumber = serial
        payload.macAddr.append(mac)
        payload.macAddrType.extend(["wifi"])
        payload.fragment = 0
        payload.userSerialNumber = 0
        payload.fetchSystemUpdates = 1

        data = gzip.compress(payload.SerializeToString())
        headers = {
            "accept-encoding": "gzip, deflate",
            "content-encoding": "gzip",
            "content-type": PROTO_TYPE,
            "user-agent": ua,
        }

        try:
            resp_raw = requests.post(CHECKIN_URL, data=data, headers=headers, timeout=15)
            resp_raw.raise_for_status()

            resp = checkin_generator_pb2.AndroidCheckinResponse()
            resp.ParseFromString(resp_raw.content)

            info = {
                "device": model,
                "variant": variant,
                "product": product,
                "found": False,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "title": None,
                "description": None,
                "size": None,
                "url": None,
            }

            for entry in resp.setting:
                name = (entry.name or b"").decode("utf-8", errors="ignore")
                value = (entry.value or b"").decode("utf-8", errors="ignore").strip()

                if name == "update_url" or "android.googleapis.com" in value:
                    info["url"] = value
                    info["found"] = True
                elif name == "update_title":
                    info["title"] = value
                elif name == "update_description":
                    info["description"] = value
                elif name == "update_size":
                    info["size"] = value

            if info["found"]:
                logger.info(f"[bold green]=======================================================[/bold green]")
                logger.info(f"[bold green][✓] LIVE FULL OTA FOUND FOR {model} ({variant})[/bold green]")
                logger.info(f"    Title: [bold cyan]{info['title']}[/bold cyan]")
                logger.info(f"    Size:  {info['size']}")
                logger.info(f"    URL:   {info['url']}")
                logger.info(f"[bold green]=======================================================[/bold green]")
                return info
            else:
                logger.warning(f"[-] No update currently advertised for {variant}.")
                return None

        except Exception as e:
            logger.error(f"[-] Checkin request error: {e}")
            return None
