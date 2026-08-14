"""
Transsion & MediaTek Hardware Database
Contains device mappings, codenames, chipsets, and OTA check-in configurations.
"""

TRANSSION_DEVICES = {
    # Infinix GT Series
    "X6871": {
        "brand": "Infinix",
        "market_name": "Infinix GT 20 Pro",
        "chipset": "MediaTek Dimensity 8200 Ultimate (MT6896)",
        "android_version": "14/15",
        "flavor": "XOS",
        "default_fingerprint": "Infinix/X6871-GL/Infinix-X6871:14/UP1A.231005.007/240508V355:user/release-keys",
        "ab_partition": True,
        "vendor_boot": True
    },
    "X6739": {
        "brand": "Infinix",
        "market_name": "Infinix GT 10 Pro",
        "chipset": "MediaTek Dimensity 8050 (MT6893)",
        "android_version": "13/14",
        "flavor": "XOS",
        "default_fingerprint": "Infinix/X6739-GL/Infinix-X6739:13/TP1A.220624.014/230720V129:user/release-keys",
        "ab_partition": True,
        "vendor_boot": True
    },
    
    # Infinix Note Series
    "X6833B": {
        "brand": "Infinix",
        "market_name": "Infinix Note 30 VIP",
        "chipset": "MediaTek Dimensity 8050 (MT6893)",
        "android_version": "13/14",
        "flavor": "XOS",
        "default_fingerprint": "Infinix/X6833B-GL/Infinix-X6833B:13/TP1A.220624.014/230510V103:user/release-keys",
        "ab_partition": True,
        "vendor_boot": True
    },
    "X6711": {
        "brand": "Infinix",
        "market_name": "Infinix Note 40 Pro+ 5G",
        "chipset": "MediaTek Dimensity 7020 (MT6855)",
        "android_version": "14",
        "flavor": "XOS",
        "default_fingerprint": "Infinix/X6711-GL/Infinix-X6711:14/UP1A.231005.007/240315V204:user/release-keys",
        "ab_partition": True,
        "vendor_boot": True
    },
    "X695C": {
        "brand": "Infinix",
        "market_name": "Infinix Note 10 Pro (ID)",
        "chipset": "MediaTek Helio G95 (MT6785)",
        "android_version": "11/12",
        "flavor": "XOS",
        "default_fingerprint": "Infinix/X695C-GL/Infinix-X695C:11/RP1A.200720.011/210609V332:user/release-keys",
        "ab_partition": True,
        "vendor_boot": False
    },
    "X6815": {
        "brand": "Infinix",
        "market_name": "Infinix Zero 5G",
        "chipset": "MediaTek Dimensity 900 (MT6877)",
        "android_version": "11/12",
        "flavor": "XOS",
        "default_fingerprint": "Infinix/X6815-GL/Infinix-X6815:11/RP1A.200720.011/220119V474:user/release-keys",
        "ab_partition": True,
        "vendor_boot": True
    },

    # TECNO Series
    "KJ7": {
        "brand": "TECNO",
        "market_name": "TECNO Spark 20 Pro+",
        "chipset": "MediaTek Helio G99 Ultimate (MT6789)",
        "android_version": "14",
        "flavor": "HiOS",
        "default_fingerprint": "TECNO/KJ7-GL/TECNO-KJ7:14/UP1A.231005.007/240118V116:user/release-keys",
        "ab_partition": True,
        "vendor_boot": True
    },
    "LH8n": {
        "brand": "TECNO",
        "market_name": "TECNO Pova 5 Pro 5G",
        "chipset": "MediaTek Dimensity 6080 (MT6833)",
        "android_version": "13/14",
        "flavor": "HiOS",
        "default_fingerprint": "TECNO/LH8n-GL/TECNO-LH8n:13/TP1A.220624.014/230714V173:user/release-keys",
        "ab_partition": True,
        "vendor_boot": True
    },
    "CK7n": {
        "brand": "TECNO",
        "market_name": "TECNO Camon 20 Pro 5G",
        "chipset": "MediaTek Dimensity 8050 (MT6893)",
        "android_version": "13/14",
        "flavor": "HiOS",
        "default_fingerprint": "TECNO/CK7n-GL/TECNO-CK7n:13/TP1A.220624.014/230425V184:user/release-keys",
        "ab_partition": True,
        "vendor_boot": True
    },
    "AD10": {
        "brand": "TECNO",
        "market_name": "TECNO Phantom V Fold",
        "chipset": "MediaTek Dimensity 9000+ (MT6983)",
        "android_version": "13/14",
        "flavor": "HiOS",
        "default_fingerprint": "TECNO/AD10-GL/TECNO-AD10:13/TP1A.220624.014/230308V115:user/release-keys",
        "ab_partition": True,
        "vendor_boot": True
    }
}

def get_device_info(model_or_codename):
    return TRANSSION_DEVICES.get(model_or_codename.upper()) or TRANSSION_DEVICES.get(model_or_codename)
