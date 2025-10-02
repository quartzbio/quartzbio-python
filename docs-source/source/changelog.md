# Changelog

## 1.2.0

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
