"""Integration tests for upload_file with multipart functionality"""

from __future__ import absolute_import

import unittest
import uuid
import os
import shutil
import tempfile
from unittest import mock

from .helper import QuartzBioTestCase
from quartzbio.errors import FileUploadError


def get_uuid_str():
    return str(uuid.uuid4())


class UploadFileMultipartIntegrationTests(QuartzBioTestCase):
    """Integration tests for upload_file method with multipart support"""

    def setUp(self):
        super(UploadFileMultipartIntegrationTests, self).setUp()
        self.tempdir = tempfile.mkdtemp(prefix="quartzbio-upload-tests-")

        # Create a test vault
        vault_name = "MultipartUploadIntegrationTests"
        self.vault = self.client.Vault.get_or_create_by_full_path(vault_name)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def create_test_file(self, size_mb=1, content_pattern="A"):
        """Create a test file of specified size"""
        filename = "{}-test-file.txt".format(get_uuid_str())
        filepath = os.path.join(self.tempdir, filename)

        with open(filepath, "w") as f:
            content = content_pattern * (1024 * 1024)  # 1MB of pattern
            for _ in range(size_mb):
                f.write(content)

        return filepath

    def test_upload_file_small_file_uses_single_part(self):
        """Test that small files use single-part upload"""
        from quartzbio.resource.object import Object

        # Create a small file (1MB - below default threshold)
        test_file = self.create_test_file(size_mb=1)

        with mock.patch.object(Object, "_upload_single_part") as mock_single_part:
            with mock.patch.object(Object, "_upload_multipart") as mock_multipart:
                mock_single_part.return_value = mock.Mock()

                Object.upload_file(
                    test_file,
                    "/",
                    self.vault.full_path,
                    multipart_threshold=2 * 1024 * 1024,  # 2MB threshold
                )

                # Verify single-part upload was used
                mock_single_part.assert_called_once()
                mock_multipart.assert_not_called()

    def test_upload_file_large_file_uses_multipart(self):
        """Test that large files use multipart upload"""
        from quartzbio.resource.object import Object

        # Create a large file (3MB - above 2MB threshold)
        test_file = self.create_test_file(size_mb=3)

        with mock.patch.object(Object, "_upload_single_part") as mock_single_part:
            with mock.patch.object(Object, "_upload_multipart") as mock_multipart:
                mock_multipart.return_value = mock.Mock()

                Object.upload_file(
                    test_file,
                    "/",
                    self.vault.full_path,
                    multipart_threshold=2 * 1024 * 1024,  # 2MB threshold
                )

                # Verify multipart upload was used
                mock_multipart.assert_called_once()
                mock_single_part.assert_not_called()

    def test_upload_file_multipart_threshold_parameter(self):
        """Test that multipart_threshold parameter is respected"""
        from quartzbio.resource.object import Object

        # Create a 1MB file
        test_file = self.create_test_file(size_mb=1)

        with mock.patch.object(Object, "_upload_single_part") as mock_single_part:
            with mock.patch.object(Object, "_upload_multipart") as mock_multipart:
                mock_multipart.return_value = mock.Mock()

                # Set threshold to 512KB - should trigger multipart for 1MB file
                Object.upload_file(
                    test_file,
                    "/",
                    self.vault.full_path,
                    multipart_threshold=512 * 1024,  # 512KB threshold
                )

                # Verify multipart upload was used
                mock_multipart.assert_called_once()
                mock_single_part.assert_not_called()

    def test_upload_file_multipart_chunksize_parameter(self):
        """Test that multipart_chunksize parameter is passed through"""
        from quartzbio.resource.object import Object

        test_file = self.create_test_file(size_mb=2)
        custom_chunk_size = 256 * 1024  # 256KB

        with mock.patch.object(Object, "_upload_multipart") as mock_multipart:
            mock_multipart.return_value = mock.Mock()

            Object.upload_file(
                test_file,
                "/",
                self.vault.full_path,
                multipart_threshold=1024 * 1024,  # 1MB threshold
                multipart_chunksize=custom_chunk_size,
            )

            # Verify multipart upload was called with custom chunk size
            mock_multipart.assert_called_once()
            call_kwargs = mock_multipart.call_args[1]
            self.assertEqual(call_kwargs.get("multipart_chunksize"), custom_chunk_size)

    def test_upload_file_multipart_fallback_preserves_other_parameters(self):
        """Test that fallback to single-part preserves other upload parameters"""
        from quartzbio.resource.object import Object

        test_file = self.create_test_file(size_mb=2)
        description = "Test file description"
        tags = ["test", "multipart"]

        with mock.patch.object(Object, "_upload_multipart") as mock_multipart:
            with mock.patch.object(Object, "_upload_single_part") as mock_single_part:
                # Mock multipart to fall back to single part
                mock_multipart.side_effect = (
                    lambda obj, path, md5, count, **kwargs: Object._upload_single_part(
                        obj, path, **kwargs
                    )
                )
                mock_single_part.return_value = mock.Mock()

                Object.upload_file(
                    test_file,
                    "/",
                    self.vault.full_path,
                    multipart_threshold=1024 * 1024,  # 1MB threshold
                    description=description,
                    tags=tags,
                )

                # Verify single-part was called with preserved parameters
                mock_single_part.assert_called()
                call_kwargs = mock_single_part.call_args[1]
                self.assertEqual(call_kwargs.get("description"), description)
                self.assertEqual(call_kwargs.get("tags"), tags)

    def test_upload_file_multipart_with_archive_folder(self):
        """Test multipart upload works with archive_folder parameter"""
        from quartzbio.resource.object import Object

        test_file = self.create_test_file(size_mb=2)

        with mock.patch.object(Object, "_upload_multipart") as mock_multipart:
            mock_multipart.return_value = mock.Mock()

            Object.upload_file(
                test_file,
                "/",
                self.vault.full_path,
                multipart_threshold=1024 * 1024,  # 1MB threshold
                archive_folder="archive",
            )

            # Verify multipart upload was called with archive_folder
            mock_multipart.assert_called_once()
            call_kwargs = mock_multipart.call_args[1]
            self.assertEqual(call_kwargs.get("archive_folder"), "archive")

    def test_upload_file_block_count_calculation(self):
        """Test that block count is correctly calculated and passed"""
        from quartzbio.resource.object import Object
        from quartzbio.utils.md5sum import md5sum

        test_file = self.create_test_file(size_mb=3)
        threshold = 1024 * 1024  # 1MB

        # Calculate expected block count
        expected_md5, expected_block_count = md5sum(
            test_file, multipart_threshold=threshold
        )

        with mock.patch.object(Object, "_upload_multipart") as mock_multipart:
            mock_multipart.return_value = mock.Mock()

            Object.upload_file(
                test_file, "/", self.vault.full_path, multipart_threshold=threshold
            )

            # Verify multipart upload was called with correct parameters
            mock_multipart.assert_called_once()
            call_args = mock_multipart.call_args[0]

            # Check that the correct MD5 and block count were passed
            self.assertEqual(call_args[2], expected_md5)  # local_md5
            self.assertEqual(call_args[3], expected_block_count)  # block_count

    def test_upload_file_zero_threshold_disables_multipart(self):
        """Test that setting multipart_threshold=0 disables multipart upload"""
        from quartzbio.resource.object import Object

        test_file = self.create_test_file(size_mb=5)  # Large file

        with mock.patch.object(Object, "_upload_single_part") as mock_single_part:
            with mock.patch.object(Object, "_upload_multipart") as mock_multipart:
                mock_single_part.return_value = mock.Mock()

                Object.upload_file(
                    test_file,
                    "/",
                    self.vault.full_path,
                    multipart_threshold=0,  # Disable multipart
                )

                # Verify single-part upload was used
                mock_single_part.assert_called_once()
                mock_multipart.assert_not_called()

    def test_upload_file_none_threshold_disables_multipart(self):
        """Test that setting multipart_threshold=None disables multipart upload"""
        from quartzbio.resource.object import Object

        test_file = self.create_test_file(size_mb=5)  # Large file

        with mock.patch.object(Object, "_upload_single_part") as mock_single_part:
            with mock.patch.object(Object, "_upload_multipart") as mock_multipart:
                mock_single_part.return_value = mock.Mock()

                Object.upload_file(
                    test_file,
                    "/",
                    self.vault.full_path,
                    multipart_threshold=None,  # Disable multipart
                )

                # Verify single-part upload was used
                mock_single_part.assert_called_once()
                mock_multipart.assert_not_called()

    def test_upload_file_multipart_progress_messages(self):
        """Test that appropriate progress messages are printed for multipart uploads"""
        from quartzbio.resource.object import Object

        test_file = self.create_test_file(size_mb=2)

        with mock.patch("builtins.print") as mock_print:
            with mock.patch.object(Object, "_upload_multipart") as mock_multipart:
                mock_multipart.return_value = mock.Mock()

                Object.upload_file(
                    test_file,
                    "/",
                    self.vault.full_path,
                    multipart_threshold=1024 * 1024,  # 1MB threshold
                )

                # Verify multipart progress message was printed
                print_calls = [str(call) for call in mock_print.call_args_list]
                multipart_message_found = any(
                    "Using multipart upload for large file" in call
                    for call in print_calls
                )
                self.assertTrue(
                    multipart_message_found,
                    "Expected multipart upload progress message not found",
                )


if __name__ == "__main__":
    unittest.main()
