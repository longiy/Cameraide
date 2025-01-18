# ❤️🎥 Cameraide - Camera Settings Manager for Blender
A Blender addon that adds custom settings for each camera with improved UI and features. Perfect for projects requiring different render settings per camera without complex render management systems.

![Image Description](https://github.com/longiy/static-assets/blob/main/cameraide-assets/Cameraid_Preview.png)

## 🎯 Purpose
Cameraide is designed to streamline workflow for artists who create multiple renders and playblasts during their work process. It's particularly valuable when:
- Multiple renders need to be compared and re-rendered
- Quick, good-quality results are needed fast
- Different cameras need different settings for previz and animatics

Note: Cameraide is not intended as a replacement for final render settings and setups, but rather as a rapid iteration tool for development and preview stages.

## ✨ Features
### 📸 Per-Camera Settings Management
- **Friend/Befriend System**: Enable/disable custom settings per camera
- **Independent Configuration**: Settings preserved even when camera inactive
- **Dual Interface**: Available in Properties panel and 3D Viewport sidebar

### 🖼️ Resolution Control
- **Custom Resolution**: Independent X/Y values per camera
- **Resolution Scale**: Percentage-based scaling (1-400%)
- **Quick Swap**: Instant aspect ratio change with one click
- **Real-time Updates**: Live viewport resolution preview

### ⏱️ Frame Range Management
- **Independent Ranges**: Custom start/end frames per camera
- **Frame Step**: Adjustable frame stepping
- **Timeline Sync**: Optional viewport timeline synchronization
- **Range Memory**: Preserves frame ranges when switching cameras

### 📂 Output Configuration
- **Path Structure**: 
  - Main output path
  - Custom subfolder per camera
  - Flexible file naming
- **Naming Options**:
  - Optional camera name prefix
  - Custom filename base
- **File Management**:
  - Overwrite protection
  - Automatic subfolder creation

### 🎨 Format Support & Settings
#### Image Formats
- **PNG**
  - Color Depth: 8/16-bit
  - Lossless compression
  - Alpha support
  - Compression level: 0-100%
  - Best for: High-quality still images requiring transparency

- **JPEG**
  - 8-bit color depth
  - Quality: 0-100%
  - Lossy compression
  - RGB color mode
  - Best for: Quick previews and web-ready images

- **OpenEXR**
  - Color Depth: 16/32-bit float
  - HDR support
  - Alpha support
  - Multiple compression options:
    - None: No compression
    - ZIP (lossless): Good compression, slower
    - PIZ (lossless): Best compression for CG images
    - RLE (lossless): Fast, good for flat areas
    - ZIPS (lossless): Single-threaded ZIP
    - PXR24 (lossy): Good for film production
    - B44/B44A (lossy): Fixed rate
    - DWAA/DWAB (lossy): High-quality lossy compression
  - Best for: Professional compositing and HDR workflows

#### Video Formats
- **MP4**
  - H.264 codec
  - High quality preset
  - Bitrate: 6000 kb/s
  - GOP size: 12
  - Best for: Web delivery and general purpose

- **MKV**
  - H.264 codec
  - High quality preset
  - Bitrate: 6000 kb/s
  - GOP size: 12
  - Best for: Large file storage and streaming

- **MOV**
  - Animation codec
  - Lossless quality
  - No compression
  - Large file size
  - Best for: Professional video editing

- **Audio Support** (for video formats)
  - Codec: MP3
  - Bitrate: 32-384 kb/s
  - Optional inclusion

### 🎬 Rendering Features
- **Dual Render Modes**:
  1. Viewport Render: Fast preview using Eevee Next
  2. Normal Render: Full quality using current engine
- **Render Settings**:
  - Transparent background toggle
  - Metadata burn-in option
  - Marker handling control
  - Progress tracking

## 🚀 Quick Start
### Basic Operations
1. Select a camera
2. Click "BEFRIEND" to enable custom settings
3. Configure resolution, frame range, and output settings
4. Use render buttons in the addon panel:
   - "Render Viewport" for quick previews
   - "Render Normal" for final quality

### 💡 Pro Tips
- Use frame range sync for easier animation preview
- Enable "Include Camera Name" for better file organization
- Utilize the viewport renderer for quick tests
- Toggle "Ignore Markers" to avoid timeline conflicts

## ⚙️ System Requirements
- Blender 4.2.0+
- Supports all render engines
- Compatible with all Blender-supported platforms

## 📝 Credits
Created by longiy
Licensed under GNU General Public License v3.0
https://github.com/longiy/Cameraide
