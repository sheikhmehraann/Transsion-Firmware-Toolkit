#!/usr/bin/env python3
"""
Quick utility to probe OTA packages specifically for the Infinix GT 20 Pro (X6871).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transsion_toolkit.prober.ota_prober import TranssionOTAProber

def main():
    print("=" * 60)
    print("  Infinix GT 20 Pro (X6871) OTA Firmware Query Utility")
    print("=" * 60)
    
    prober = TranssionOTAProber(model="X6871")
    ota_info = prober.probe_ota(target_version="15.1.2.180SP05")
    
    print("\n[+] Firmware Payload Info:")
    for k, v in ota_info.items():
        print(f"    {k:18}: {v}")

if __name__ == "__main__":
    main()
