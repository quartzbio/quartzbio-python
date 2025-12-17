# Changelog

## 1.4.0

- Removed file upload threshold in order to fix the Dataset Imports using manifest URLs
- Fixed EDP file paths for Windows file upload command

## 1.3.0

- Improved multipart upload resilience by introducing the retries of the failed part by requesting a new pre-signed URL from the EDP API, instead of aborting the entire upload process in case when a specific part fails during a multipart upload
- Clean-fail on read-only log files, ensuring permission issues are detected and reported before further package usages

## 1.2.0 

- Update minimum required python version to 3.8
- Add api_host property to the Client class for easier access to the configured API host
- Add support for configuring the client via environment variables, and local credentials file
- Add support for multipart uploads for large files

- Update minimum required python version to 3.8
- Add api_host property to the Client class for easier access to the configured API host
- Add support for configuring the client via environment variables, and local credentials file
- Add support for multipart uploads for large files

## 1.1.0

- Fix annotator_params default to empty dict instead of None
- Fix credentials handling when both API key and access token are provided
- Fix uploads paths when used on Windows OS

## 1.0.0

- Initial release
