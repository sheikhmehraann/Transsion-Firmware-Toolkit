import os
import sys
import tarfile
import subprocess
import shutil
from transsion_toolkit.core.logger import logger

class ZstdPackager:
    """
    Packs extracted partition .img files into a high-ratio .tar.zst archive,
    identical to the releases published on SourceForge by Rama Bondan Prakoso (e.g. X6871-...-images.tar.zst).
    """

    def __init__(self, compression_level=19, threads=0):
        self.compression_level = compression_level
        self.threads = threads

    def pack_images(self, images_dir, output_archive_path):
        logger.info(f"[*] Packaging partition images from '{images_dir}' into: [bold cyan]{output_archive_path}[/bold cyan]")
        
        if not os.path.exists(images_dir):
            raise FileNotFoundError(f"Directory not found: {images_dir}")

        img_files = [f for f in os.listdir(images_dir) if f.endswith(".img")]
        if not img_files:
            raise FileNotFoundError(f"No .img partition files found in '{images_dir}'")

        logger.info(f"[*] Found {len(img_files)} partition images to pack:")
        total_raw_size = 0
        for img in sorted(img_files):
            sz = os.path.getsize(os.path.join(images_dir, img))
            total_raw_size += sz
            logger.info(f"    - {img} ({sz / (1024*1024):.2f} MB)")

        logger.info(f"[*] Total Uncompressed Size: {total_raw_size / (1024*1024):.2f} MB")

        # Try native tar + zstd pipeline
        if shutil.which("zstd") and shutil.which("tar"):
            logger.info(f"[*] Using native multi-threaded zstd (level {self.compression_level})...")
            # In Linux/Unix/Git Bash
            tar_cmd = f"tar -cf - -C {images_dir} {' '.join(img_files)} | zstd -T{self.threads} -{self.compression_level} -o {output_archive_path}"
            subprocess.run(tar_cmd, shell=True, check=True)
        else:
            logger.info("[*] Running embedded Python Tar + Zstandard compression...")
            try:
                import zstandard as zstd
                cctx = zstd.ZstdCompressor(level=self.compression_level, threads=self.threads)
                
                temp_tar = output_archive_path + ".tmp.tar"
                with tarfile.open(temp_tar, "w") as tar:
                    for img in img_files:
                        img_path = os.path.join(images_dir, img)
                        tar.add(img_path, arcname=img)
                
                with open(temp_tar, "rb") as f_in, open(output_archive_path, "wb") as f_out:
                    cctx.copy_stream(f_in, f_out)
                
                os.remove(temp_tar)
            except ImportError:
                # Fallback to standard tar.gz if zstandard python library not yet installed
                logger.warning("[!] zstandard python module not found. Falling back to tar.gz...")
                fallback_path = output_archive_path.replace(".tar.zst", ".tar.gz")
                with tarfile.open(fallback_path, "w:gz") as tar:
                    for img in img_files:
                        tar.add(os.path.join(images_dir, img), arcname=img)
                output_archive_path = fallback_path

        compressed_size = os.path.getsize(output_archive_path)
        logger.info(f"[bold green][✓] Archive Created Successfully: {output_archive_path}[/bold green]")
        logger.info(f"    Compressed Size:   {compressed_size / (1024*1024):.2f} MB")
        logger.info(f"    Compression Ratio: { (1 - compressed_size / total_raw_size) * 100:.1f}% space saved")

        return output_archive_path

    def unpack_archive(self, archive_path, output_dir="unpacked_images"):
        logger.info(f"[*] Decompressing {archive_path} into '{output_dir}'...")
        os.makedirs(output_dir, exist_ok=True)
        
        if shutil.which("zstd") and shutil.which("tar"):
            cmd = f"zstd -d {archive_path} --stdout | tar -xf - -C {output_dir}"
            subprocess.run(cmd, shell=True, check=True)
        else:
            import zstandard as zstd
            dctx = zstd.ZstdDecompressor()
            temp_tar = archive_path + ".tmp.tar"
            with open(archive_path, "rb") as f_in, open(temp_tar, "wb") as f_out:
                dctx.copy_stream(f_in, f_out)
            
            with tarfile.open(temp_tar, "r") as tar:
                tar.extractall(output_dir)
            os.remove(temp_tar)
        
        logger.info(f"[bold green][✓] Decompressed {len(os.listdir(output_dir))} images into '{output_dir}'[/bold green]")
        return output_dir
