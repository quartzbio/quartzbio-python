"""Test cases for multipart upload functionality"""

from __future__ import absolute_import

import unittest
import uuid
import os
import shutil
import tempfile
import hashlib
import base64
import binascii
from unittest import mock

import requests

from .helper import QuartzBioTestCase
from quartzbio.test.client_mocks import fake_object_create
from quartzbio.errors import QuartzBioError, FileUploadError
from quartzbio.utils.md5sum import MULTIPART_THRESHOLD, MULTIPART_CHUNKSIZE


def get_uuid_str():
    return str(uuid.uuid4())


class MockResponse:
    """Mock HTTP response for testing"""

    def __init__(self, status_code=200, headers=None, content=b""):
        self.status_code = status_code
        self.headers = headers or {}
        self.content = content


class MultipartUploadTests(QuartzBioTestCase):
    """Test cases for the _upload_multipart method"""

    def setUp(self):
        super(MultipartUploadTests, self).setUp()
        self.tempdir = tempfile.mkdtemp(prefix="quartzbio-multipart-tests-")

        # Create a mock object for testing
        self.mock_obj = mock.Mock()
        self.mock_obj.instance_url.return_value = "/objects/12345"
        self.mock_obj.delete = mock.Mock()

        # Mock client
        self.mock_client = mock.Mock()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def create_test_file(self, size_mb=1, content_pattern=b"A"):
        """Create a test file of specified size"""
        filename = "{}-test-file.bin".format(get_uuid_str())
        filepath = os.path.join(self.tempdir, filename)

        with open(filepath, "wb") as f:
            chunk_size = 1024 * 1024  # 1MB chunks
            for _ in range(size_mb):
                f.write(content_pattern * chunk_size)

        return filepath

    def test_multipart_upload_success(self):
        """Test successful multipart upload"""
        from quartzbio.resource.object import Object

        # Create a test file larger than multipart threshold
        test_file = self.create_test_file(size_mb=5)  # 5MB file

        # Calculate expected MD5
        local_md5, block_count = self._calculate_multipart_md5(test_file)

        # Mock API responses
        upload_id = "test-upload-id-123"
        part_urls = [
            "https://s3.amazonaws.com/bucket/part1",
            "https://s3.amazonaws.com/bucket/part2",
            "https://s3.amazonaws.com/bucket/part3",
        ]

        # Mock initiate multipart upload response
        self.mock_client.post.side_effect = [
            {"upload_id": upload_id, "part_urls": part_urls},
            {"status": "completed"},
        ]

        # Mock HTTP PUT requests for parts
        with mock.patch("requests.Session") as mock_session_class:
            mock_session = mock.Mock()
            mock_session_class.return_value = mock_session

            # Mock successful part uploads
            mock_put_response = MockResponse(
                status_code=200, headers={"ETag": "test-etag-123"}
            )
            mock_session.put.return_value = mock_put_response

            # Call the method under test
            result = Object._upload_multipart(
                self.mock_obj,
                test_file,
                local_md5,
                block_count,
                client=self.mock_client,
            )

            # Verify the result
            self.assertEqual(result, self.mock_obj)

            # Verify API calls
            self.assertEqual(self.mock_client.post.call_count, 2)

            # Verify initiate multipart upload call
            init_call = self.mock_client.post.call_args_list[0]
            self.assertEqual(init_call[0][0], "/objects/12345/multipart-upload")
            self.assertEqual(init_call[0][1]["parts"], block_count)

            # Verify complete multipart upload call
            complete_call = self.mock_client.post.call_args_list[1]
            self.assertEqual(
                complete_call[0][0], "/objects/12345/multipart-upload/complete"
            )
            complete_data = complete_call[0][1]
            self.assertEqual(complete_data["upload_id"], upload_id)
            self.assertEqual(complete_data["md5"], local_md5)
            self.assertEqual(len(complete_data["parts"]), block_count)

    def test_multipart_upload_api_not_supported(self):
        """Test fallback when multipart API returns 404"""
        from quartzbio.resource.object import Object

        test_file = self.create_test_file(size_mb=2)
        local_md5, block_count = self._calculate_multipart_md5(test_file)

        # Mock 404 error for multipart API
        not_found_error = QuartzBioError("Not found")
        not_found_error.status_code = 404
        self.mock_client.post.side_effect = not_found_error

        # Mock the fallback method
        with mock.patch.object(Object, "_upload_single_part") as mock_single_part:
            mock_single_part.return_value = self.mock_obj

            result = Object._upload_multipart(
                self.mock_obj,
                test_file,
                local_md5,
                block_count,
                client=self.mock_client,
            )

            # Verify fallback was called
            self.assertEqual(result, self.mock_obj)
            mock_single_part.assert_called_once_with(
                self.mock_obj, test_file, client=self.mock_client
            )

    def test_multipart_upload_init_failure(self):
        """Test fallback when multipart initialization fails"""
        from quartzbio.resource.object import Object

        test_file = self.create_test_file(size_mb=2)
        local_md5, block_count = self._calculate_multipart_md5(test_file)

        # Mock failed initialization (missing upload_id)
        self.mock_client.post.return_value = {"part_urls": []}

        # Mock the fallback method
        with mock.patch.object(Object, "_upload_single_part") as mock_single_part:
            mock_single_part.return_value = self.mock_obj

            result = Object._upload_multipart(
                self.mock_obj,
                test_file,
                local_md5,
                block_count,
                client=self.mock_client,
            )

            # Verify fallback was called
            self.assertEqual(result, self.mock_obj)
            mock_single_part.assert_called_once()

    def test_multipart_upload_part_failure(self):
        """Test error handling when a part upload fails"""
        from quartzbio.resource.object import Object

        test_file = self.create_test_file(size_mb=2)
        local_md5, block_count = self._calculate_multipart_md5(test_file)

        upload_id = "test-upload-id-456"
        part_urls = ["https://s3.amazonaws.com/bucket/part1"]

        # Mock successful initiate
        self.mock_client.post.return_value = {
            "upload_id": upload_id,
            "part_urls": part_urls,
        }

        # Mock failed part upload
        with mock.patch("requests.Session") as mock_session_class:
            mock_session = mock.Mock()
            mock_session_class.return_value = mock_session

            # Mock failed PUT request
            mock_put_response = MockResponse(status_code=500, content=b"Server Error")
            mock_session.put.return_value = mock_put_response

            # Expect FileUploadError
            with self.assertRaises(FileUploadError) as context:
                Object._upload_multipart(
                    self.mock_obj,
                    test_file,
                    local_md5,
                    block_count,
                    client=self.mock_client,
                )

            # Verify error message
            self.assertIn("Failed to upload part 1", str(context.exception))

            # Verify cleanup was attempted
            self.mock_client.delete.assert_called_once_with(
                "/objects/12345/multipart-upload", {"upload_id": upload_id}
            )
            self.mock_obj.delete.assert_called_once_with(force=True)

    def test_multipart_upload_complete_failure(self):
        """Test error handling when complete multipart upload fails"""
        from quartzbio.resource.object import Object

        test_file = self.create_test_file(size_mb=2)
        local_md5, block_count = self._calculate_multipart_md5(test_file)

        upload_id = "test-upload-id-789"
        part_urls = ["https://s3.amazonaws.com/bucket/part1"]

        # Mock responses
        self.mock_client.post.side_effect = [
            {"upload_id": upload_id, "part_urls": part_urls},
            {"status": "failed", "error": "Complete failed"},
        ]

        # Mock successful part upload
        with mock.patch("requests.Session") as mock_session_class:
            mock_session = mock.Mock()
            mock_session_class.return_value = mock_session

            mock_put_response = MockResponse(
                status_code=200, headers={"ETag": "test-etag"}
            )
            mock_session.put.return_value = mock_put_response

            # Expect FileUploadError
            with self.assertRaises(FileUploadError) as context:
                Object._upload_multipart(
                    self.mock_obj,
                    test_file,
                    local_md5,
                    block_count,
                    client=self.mock_client,
                )

            # Verify error message
            self.assertIn("Failed to complete multipart upload", str(context.exception))

    def test_multipart_upload_with_custom_chunk_size(self):
        """Test multipart upload with custom chunk size"""
        from quartzbio.resource.object import Object

        test_file = self.create_test_file(size_mb=1)
        local_md5, _ = self._calculate_multipart_md5(test_file)

        # Use custom chunk size
        custom_chunk_size = 512 * 1024  # 512KB
        block_count = 2  # For 1MB file with 512KB chunks

        upload_id = "test-upload-id-custom"
        part_urls = [
            "https://s3.amazonaws.com/bucket/part1",
            "https://s3.amazonaws.com/bucket/part2",
        ]

        self.mock_client.post.side_effect = [
            {"upload_id": upload_id, "part_urls": part_urls},
            {"status": "completed"},
        ]

        with mock.patch("requests.Session") as mock_session_class:
            mock_session = mock.Mock()
            mock_session_class.return_value = mock_session

            mock_put_response = MockResponse(
                status_code=200, headers={"ETag": "test-etag"}
            )
            mock_session.put.return_value = mock_put_response

            # Call with custom chunk size
            result = Object._upload_multipart(
                self.mock_obj,
                test_file,
                local_md5,
                block_count,
                multipart_chunksize=custom_chunk_size,
                client=self.mock_client,
            )

            self.assertEqual(result, self.mock_obj)

            # Verify that the correct number of parts were uploaded
            self.assertEqual(mock_session.put.call_count, block_count)

    def test_multipart_upload_retry_logic(self):
        """Test retry logic for failed part uploads"""
        from quartzbio.resource.object import Object

        test_file = self.create_test_file(size_mb=1)
        local_md5, block_count = self._calculate_multipart_md5(test_file)

        upload_id = "test-upload-id-retry"
        part_urls = ["https://s3.amazonaws.com/bucket/part1"]

        self.mock_client.post.side_effect = [
            {"upload_id": upload_id, "part_urls": part_urls},
            {"status": "completed"},
        ]

        with mock.patch("requests.Session") as mock_session_class:
            mock_session = mock.Mock()
            mock_session_class.return_value = mock_session

            # Verify retry configuration
            with mock.patch("requests.adapters.HTTPAdapter") as mock_adapter_class:
                mock_adapter = mock.Mock()
                mock_adapter_class.return_value = mock_adapter

                mock_put_response = MockResponse(
                    status_code=200, headers={"ETag": "test-etag"}
                )
                mock_session.put.return_value = mock_put_response

                Object._upload_multipart(
                    self.mock_obj,
                    test_file,
                    local_md5,
                    block_count,
                    client=self.mock_client,
                )

                # Verify retry configuration was set up
                mock_adapter_class.assert_called()
                mock_session.mount.assert_called_with("https://", mock_adapter)

    def test_multipart_upload_md5_calculation(self):
        """Test that MD5 headers are correctly calculated for parts"""
        from quartzbio.resource.object import Object

        test_file = self.create_test_file(size_mb=1)
        local_md5, block_count = self._calculate_multipart_md5(test_file)

        upload_id = "test-upload-id-md5"
        part_urls = ["https://s3.amazonaws.com/bucket/part1"]

        self.mock_client.post.side_effect = [
            {"upload_id": upload_id, "part_urls": part_urls},
            {"status": "completed"},
        ]

        with mock.patch("requests.Session") as mock_session_class:
            mock_session = mock.Mock()
            mock_session_class.return_value = mock_session

            mock_put_response = MockResponse(
                status_code=200, headers={"ETag": "test-etag"}
            )
            mock_session.put.return_value = mock_put_response

            Object._upload_multipart(
                self.mock_obj,
                test_file,
                local_md5,
                block_count,
                client=self.mock_client,
            )

            # Verify MD5 header was set correctly
            put_call = mock_session.put.call_args
            headers = put_call[1]["headers"]

            self.assertIn("Content-MD5", headers)
            self.assertIn("Content-Length", headers)

            # Verify MD5 is base64 encoded
            content_md5 = headers["Content-MD5"]
            self.assertIsInstance(content_md5, bytes)

    def test_multipart_upload_cleanup_on_exception(self):
        """Test that cleanup occurs when an unexpected exception happens"""
        from quartzbio.resource.object import Object

        test_file = self.create_test_file(size_mb=1)
        local_md5, block_count = self._calculate_multipart_md5(test_file)

        upload_id = "test-upload-id-cleanup"
        part_urls = ["https://s3.amazonaws.com/bucket/part1"]

        self.mock_client.post.return_value = {
            "upload_id": upload_id,
            "part_urls": part_urls,
        }

        # Mock exception during file reading
        with mock.patch("builtins.open", side_effect=IOError("File read error")):
            with self.assertRaises(FileUploadError) as context:
                Object._upload_multipart(
                    self.mock_obj,
                    test_file,
                    local_md5,
                    block_count,
                    client=self.mock_client,
                )

            # Verify cleanup was attempted
            self.mock_client.delete.assert_called_once_with(
                "/objects/12345/multipart-upload", {"upload_id": upload_id}
            )
            self.mock_obj.delete.assert_called_once_with(force=True)

            # Verify error message includes original exception
            self.assertIn("File read error", str(context.exception))

    def test_multipart_upload_empty_file(self):
        """Test behavior with an empty file"""
        from quartzbio.resource.object import Object

        # Create empty file
        test_file = os.path.join(self.tempdir, "empty-file.txt")
        with open(test_file, "w") as f:
            pass  # Create empty file

        local_md5 = hashlib.md5().hexdigest()
        block_count = 0

        upload_id = "test-upload-id-empty"

        self.mock_client.post.side_effect = [
            {"upload_id": upload_id, "part_urls": []},
            {"status": "completed"},
        ]

        result = Object._upload_multipart(
            self.mock_obj, test_file, local_md5, block_count, client=self.mock_client
        )

        self.assertEqual(result, self.mock_obj)

        # Verify complete was called even with no parts
        complete_call = self.mock_client.post.call_args_list[1]
        complete_data = complete_call[0][1]
        self.assertEqual(len(complete_data["parts"]), 0)

    def _calculate_multipart_md5(self, filepath):
        """Helper to calculate multipart MD5 and block count"""
        from quartzbio.utils.md5sum import md5sum

        return md5sum(filepath, multipart_threshold=MULTIPART_THRESHOLD)


if __name__ == "__main__":
    unittest.main()
