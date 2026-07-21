"""
File utilities for Dreamcobots platform.

Provides high-performance helpers for chunked large-file I/O,
metadata extraction, integrity checking, and file compression.
"""

import hashlib
import io
import os
import zipfile
from typing import Generator, List, Optional, Tuple


# Default chunk size: 8 MB (optimised for large file throughput)
DEFAULT_CHUNK_SIZE = 8 * 1024 * 1024


class FileUtils:
    """
    Best-in-class file utilities for the largest file sizes and fastest access.

    All methods operate on file paths or raw bytes and are designed to be
    memory-efficient by processing data in configurable chunks.
    """

    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE) -> None:
        self.chunk_size = chunk_size

    # ------------------------------------------------------------------
    # Reading / writing
    # ------------------------------------------------------------------

    def read_chunks(self, file_path: str) -> Generator[bytes, None, None]:
        """
        Yield the contents of *file_path* in chunks.

        Args:
            file_path: Absolute or relative path to a file.

        Yields:
            Successive byte chunks of size ``self.chunk_size``.
        """
        with open(file_path, "rb") as fh:
            while True:
                chunk = fh.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk

    def write_chunks(self, file_path: str, chunks: Generator[bytes, None, None]) -> int:
        """
        Write yielded chunks to *file_path*.

        Args:
            file_path: Destination path.
            chunks: Generator of byte chunks.

        Returns:
            Total bytes written.
        """
        total = 0
        with open(file_path, "wb") as fh:
            for chunk in chunks:
                fh.write(chunk)
                total += len(chunk)
        return total

    def copy_large_file(self, src: str, dst: str) -> int:
        """
        Copy *src* to *dst* using chunked I/O. Returns bytes copied.
        """
        return self.write_chunks(dst, self.read_chunks(src))

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def get_metadata(self, file_path: str) -> dict:
        """
        Return basic metadata for *file_path*.

        Returns:
            Dict with keys: path, size_bytes, size_mb, extension, exists.
        """
        exists = os.path.isfile(file_path)
        size = os.path.getsize(file_path) if exists else 0
        _, ext = os.path.splitext(file_path)
        return {
            "path": file_path,
            "size_bytes": size,
            "size_mb": round(size / (1024 * 1024), 4),
            "extension": ext.lower(),
            "exists": exists,
        }

    # ------------------------------------------------------------------
    # Integrity
    # ------------------------------------------------------------------

    def checksum(self, file_path: str, algorithm: str = "sha256") -> str:
        """
        Compute the checksum of *file_path*.

        Args:
            file_path: Path to the file.
            algorithm: Hash algorithm name accepted by ``hashlib`` (default sha256).

        Returns:
            Hex-encoded digest string.
        """
        h = hashlib.new(algorithm)
        for chunk in self.read_chunks(file_path):
            h.update(chunk)
        return h.hexdigest()

    def verify_integrity(self, file_path: str, expected_checksum: str, algorithm: str = "sha256") -> bool:
        """
        Return True if the file checksum matches *expected_checksum*.
        """
        return self.checksum(file_path, algorithm) == expected_checksum

    # ------------------------------------------------------------------
    # Compression
    # ------------------------------------------------------------------

    def compress(self, file_paths: List[str], archive_path: str) -> str:
        """
        Create a ZIP archive at *archive_path* containing all listed files.

        Args:
            file_paths: List of file paths to include.
            archive_path: Destination archive path (must end in .zip).

        Returns:
            The archive path.
        """
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for fp in file_paths:
                zf.write(fp, arcname=os.path.basename(fp))
        return archive_path

    def decompress(self, archive_path: str, destination_dir: str) -> List[str]:
        """
        Extract a ZIP archive to *destination_dir*.

        Returns:
            List of extracted file paths.
        """
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(destination_dir)
            return [os.path.join(destination_dir, name) for name in zf.namelist()]

    # ------------------------------------------------------------------
    # Bytes helpers (for in-memory operations / testing)
    # ------------------------------------------------------------------

    @staticmethod
    def checksum_bytes(data: bytes, algorithm: str = "sha256") -> str:
        """Return the checksum of raw *data* bytes."""
        h = hashlib.new(algorithm)
        h.update(data)
        return h.hexdigest()

    @staticmethod
    def split_bytes(data: bytes, chunk_size: int = DEFAULT_CHUNK_SIZE) -> List[bytes]:
        """Split *data* into a list of chunks of at most *chunk_size* bytes."""
        return [data[i: i + chunk_size] for i in range(0, len(data), chunk_size)]
