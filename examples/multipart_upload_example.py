#!/usr/bin/env python3
"""
Example usage of the new multipart upload functionality in QuartzBio Object.upload_file()

This demonstrates how files larger than the multipart_threshold (default 64MB)
will automatically use multipart upload for better reliability and performance.
"""

from quartzbio import Object
from quartzbio.errors import FileUploadError, QuartzBioError


def upload_with_multipart_example():
    """Example of uploading files with automatic multipart detection"""

    # Upload a small file - will use single-part upload
    small_file = Object.upload_file(
        local_path="/path/to/small_file.csv",
        remote_path="/",
        vault_full_path="~/my_vault",
    )
    print(f"Small file uploaded: {small_file.full_path}")

    # Upload a large file - will automatically use multipart upload if > 64MB
    large_file = Object.upload_file(
        local_path="/path/to/large_file.zip",
        remote_path="/data/",
        vault_full_path="~/my_vault",
        description="Large dataset file",
    )
    print(f"Large file uploaded: {large_file.full_path}")

    # Customize multipart threshold and chunk size
    custom_upload = Object.upload_file(
        local_path="/path/to/custom_file.tar.gz",
        remote_path="/backups/",
        vault_full_path="~/my_vault",
        multipart_threshold=32 * 1024 * 1024,  # 32MB threshold
        multipart_chunksize=128 * 1024 * 1024,  # 128MB chunks
        tags=["backup", "compressed"],
    )
    print(f"Custom upload completed: {custom_upload.full_path}")


def upload_with_error_handling():
    """Example with proper error handling for multipart uploads"""

    try:
        obj = Object.upload_file(
            local_path="/path/to/very_large_file.dat",
            remote_path="/uploads/",
            vault_full_path="~/my_vault",
        )
        print(f"Upload successful: {obj.full_path}")

    except FileUploadError as e:
        print(f"Upload failed: {e}")
        # Handle upload failure (file cleanup is automatic)

    except QuartzBioError as e:
        print(f"API error: {e}")
        # Handle API-related errors


if __name__ == "__main__":
    print("QuartzBio Multipart Upload Examples")
    print("===================================")

    print("\n1. Basic multipart upload example:")
    # upload_with_multipart_example()  # Commented out - requires actual files

    print("\n2. Error handling example:")
    # upload_with_error_handling()  # Commented out - requires actual files

    print("\nFeatures added:")
    print("- Automatic multipart upload for files > 64MB (configurable)")
    print("- Graceful fallback to single-part upload if multipart API unavailable")
    print("- Configurable chunk size and threshold")
    print("- Progress reporting during multipart upload")
    print("- Automatic cleanup on upload failure")
    print("- Retry logic for individual parts")
