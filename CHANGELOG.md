# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[1.0.0]: https://github.com/rennf93/cutie-pi/releases/tag/v1.0.0
