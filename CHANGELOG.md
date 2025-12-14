# Changelog

## [1.1.0] - 2025-12-14

### Fixed
- **GitHub Actions Ubuntu 24.04 Compatibility**: Fixed Playwright dependency installation
  - Changed `libasound2` to `libasound2t64` for Ubuntu 24.04
  - Added explicit package list with t64 variants
  - Split dependency installation into separate steps for better error handling

### Changed
- Increased stream loading wait time from 20s to 25s for better reliability
- Improved error messages in workflow

### Technical Details
Ubuntu 24.04 renamed several packages with `t64` suffix for 64-bit time_t support:
- `libasound2` → `libasound2t64`
- `libatk1.0-0` → `libatk1.0-0t64`
- `libatk-bridge2.0-0` → `libatk-bridge2.0-0t64`
- `libcups2` → `libcups2t64`
- `libatspi2.0-0` → `libatspi2.0-0t64`
- `libglib2.0-0` → `libglib2.0-0t64`
- `libgtk-3-0` → `libgtk-3-0t64`

## [1.0.0] - 2025-12-14

### Added
- Initial release
- Playwright-based web scraper for cricket streams
- m3u8 link extraction with headers
- Firebase RTDB integration
- GitHub Actions workflow (40-minute schedule)
- Iframe and redirect handling
- Comprehensive documentation
- Local testing scripts

### Features
- Automated scraping every 40 minutes
- Network request interception
- Header extraction (Origin, Referer, User-Agent)
- Manual workflow trigger support
- Artifact storage (7-day retention)
- Detailed logging and error handling
