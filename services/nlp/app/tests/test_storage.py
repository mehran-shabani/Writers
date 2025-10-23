"""Tests for storage module."""
import pytest
from unittest.mock import Mock, patch
from app.storage import upload_bytes, presign, download_to_bytes


@patch("app.storage.s3")
def test_upload_bytes_success(mock_s3):
    """Test successful file upload."""
    key = upload_bytes("test/key.txt", b"content", "text/plain")
    assert key == "test/key.txt"
    mock_s3.put_object.assert_called_once()


@patch("app.storage.s3")
def test_presign_url(mock_s3):
    """Test presigned URL generation."""
    mock_s3.generate_presigned_url.return_value = "https://example.com/signed"
    url = presign("test/key.txt")
    assert url == "https://example.com/signed"
    mock_s3.generate_presigned_url.assert_called_once()


@patch("app.storage.s3")
def test_download_to_bytes_success(mock_s3):
    """Test successful file download."""
    mock_body = Mock()
    mock_body.read.return_value = b"content"
    mock_s3.get_object.return_value = {"Body": mock_body}
    
    data = download_to_bytes("test/key.txt")
    assert data == b"content"
    mock_s3.get_object.assert_called_once()
