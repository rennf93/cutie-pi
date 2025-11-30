# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-30

### Added
- Settings persistence: all settings now save to config file when locking the settings screen
- New config options: `CUTIE_SCREEN_TIMEOUT`, `CUTIE_SCANLINES`, `CUTIE_SHOW_FPS`, `CUTIE_BRIGHTNESS`

### Fixed
- Fixed display sleep for PiTFT and other non-standard displays:
  - Added framebuffer blanking support (`/sys/class/graphics/fb0/blank`)
  - Added more backlight control paths for various display types
  - Added brightness-based sleep (saves and restores brightness level)
  - Improved error handling and logging for sleep/wake methods

### Changed
- Settings now persist across reboots (saved when user locks the settings screen)

## [1.0.2] - 2025-11-30

### Added
- Centralized `Layout` class in config.py for true resolution independence
- Font scaling system that adjusts text size based on screen dimensions

### Fixed
- Fixed 2.8" PiTFT (240x320) display support with proper scaling
- Settings screen arrows and tap zones now fully responsive (were hardcoded off-screen for small displays)
- All UI elements now scale proportionally across different screen sizes
- Font sizes scale down on smaller screens to prevent text overflow

### Changed
- All screen files now use Layout class for consistent responsive positioning
- Minimum font sizes enforced to maintain readability on small screens

## [1.0.1] - 2025-11-25

### Fixed
- Fixed 5-inch display (800x480) support by making PI-HOLE stats and System screens responsive
- UI coordinates now scale properly based on SCREEN_WIDTH and SCREEN_HEIGHT configuration

## [1.0.0] - 2025-01-20

### Added
- Initial release of Cutie-Pi dashboard for Pi-hole
- Real-time Pi-hole statistics display (queries, blocked, clients, blocklist size)
- System information screen (CPU, RAM, temperature, disk, uptime, fan speed)
- Query history graph with total and blocked queries
- Top blocked domains list
- Top clients list
- Settings screen with runtime configuration
  - Theme selection
  - Scanlines toggle
  - FPS display toggle
  - Brightness control
  - API refresh interval
  - Screen timeout
- Settings lock feature to prevent accidental changes
- Display sleep/wake on touch
- 9 unique themes with distinct visual styles:
  - **default** - Classic Pi-hole multi-color (pixel style)
  - **monochrome** - Clean white/gray (pixel style)
  - **neon** - Hot pink/magenta with glow effects
  - **ocean** - Blue with dashed borders
  - **sunset** - Golden orange with thick borders
  - **matrix** - Green with terminal-style brackets
  - **cyberpunk** - Pink/cyan with double borders
  - **666** - Pure red with inverted/inset borders
  - **arcade** - Retrowave purple/pink/gold with glow effects
- Swipe navigation between screens
- Automatic Pi-hole API authentication
- Environment variable configuration support
- Systemd service integration
- Installation and uninstallation scripts

### Technical Features
- Pygame-based rendering optimized for 480x320 displays
- Modular screen architecture with base class
- Dynamic color system with theme-aware rendering
- Multiple border styles (pixel, glow, dashed, double, thick, terminal, inverted)
- Multiple bar styles matching each theme
- Smooth counter animations
- CRT scanline effect (optional)

### Supported Hardware
- Raspberry Pi 3/4/5
- 3.5" LCD touchscreen (480x320)
- Compatible with Pi-hole v6 API

[1.1.0]: https://github.com/rennf93/cutie-pi/releases/tag/v1.1.0
[1.0.2]: https://github.com/rennf93/cutie-pi/releases/tag/v1.0.2
[1.0.1]: https://github.com/rennf93/cutie-pi/releases/tag/v1.0.1
[1.0.0]: https://github.com/rennf93/cutie-pi/releases/tag/v1.0.0
