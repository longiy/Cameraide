# Cameraide 
Cameraide fills the gap between Blender's basic render settings and complex render management systems. It's perfect for projects where you need more control than default settings offer, but don't want the overhead of a full render management pipeline.

## Cameraide v0.1.3
- Added basic support for video export (MP4,MOV,MKV) with audio (MP3)
- Rendering refactor, now it should be faster
- Major, frame range sync improvement it should be more stable

## Cameraide v0.1.2
- Rendering refactor

## Cameraide v0.1.1
- Initial Release

## What it does

Saves render settings per camera, including:
- Resolution and frame ranges
- Output paths and file names
- Format settings (PNG/JPG/EXR)

Helpful for:
- Rendering multiple sequences with different settings from one file
- Quick play blasts with varying frame ranges
- Avoiding manual settings adjustment when switching between cameras

![Image Description](https://github.com/longiy/static-assets/blob/main/cameraide-assets/Cameraid_Preview.png)

## Features
### 🎥 Per-Camera Custom Settings
- Enable/disable custom settings for each camera using the "BEFRIEND/FRIEND" toggle
- Settings are preserved even when the camera is not active
- Independent configuration for each camera in your scene

### 📐 Resolution Management
- Custom resolution settings per camera
- Resolution scale percentage control
- Quick resolution swap button for instant aspect ratio changes
- Real-time viewport resolution updates

### ⏱️ Frame Range Control
- Independent frame ranges for each camera
- Custom frame step settings
- Sync option to automatically update viewport timeline with camera's frame range
- Frame range synchronization toggle

### 📂 Output Configuration
- Custom output folder per camera
- Customizable file naming
- Option to include camera name in filenames
- Overwrite protection toggle
- Support for multiple output formats:
  - PNG
  - JPEG
  - OpenEXR
  - FFMPEG (Video)

### 🎨 Format-Specific Settings
#### PNG Options
- Color modes: BW, RGB, RGBA
- Color depth: 8-bit, 16-bit
- Compression level control

#### JPEG Options
- Color modes: BW, RGB
- Quality level adjustment

#### OpenEXR Options
- Color modes: BW, RGB, RGBA
- Color depth: Half (16-bit), Full (32-bit)
- Multiple codec options:
  - None
  - Pxr24 (lossy)
  - ZIP (lossless)
  - PIZ (lossless)
  - RLE (lossless)
  - ZIPS (lossless)
  - B44/B44A (lossy)
  - DWAA/DWAB (lossy)
- Preview image generation option

#### Video Output Options (FFMPEG)
- Container formats:
  - QuickTime
  - MPEG-4
  - Matroska
- Video codecs:
  - H.264/AVC
  - PNG
  - QuickTime Animation
- Quality settings for H.264:
  - Constant Rate Factor (CRF) presets: Lossless, Perceptually Lossless, High, Medium, Low
  - Manual bitrate control with min/max rates
  - GOP size adjustment
  - Encoding speed presets: Fast, Medium, Slow
- Audio options:
  - Codec: MP3
  - Configurable bitrate (32-384 kb/s)
  - Option to disable audio

### 🎬 Rendering Features
- Two rendering modes:
  1. **Viewport Render**: Fast rendering using Eevee Next
  2. **Normal Render**: Full render using current render engine
- Transparent background toggle
- Metadata burn-in option
- Marker handling during rendering (to avoid clash with camera markers)
- Progress tracking during render

### 🖥️ Interface Options
- Available in two locations:
  1. Properties > Camera > Cameraide
  2. 3D View > Sidebar > Cameraide
- Intuitive UI with organized sections
- Clear visual feedback for active settings

## Installation

1. Download the latest release
2. In Blender, go to Edit > Preferences > Get Extensions
3. Use the drop-down menu in the top right, or drag-and-drop an extension .zip package into Blender.

## Usage

1. Select a camera in your scene
2. Click the "BEFRIEND" button to enable custom settings
3. Adjust the desired settings in either the Properties panel or 3D View sidebar
4. Use the render buttons to output your frames:
   - "Render Viewport" for quick renders using Eevee Next
   - "Render Normal" for full quality renders using your current render engine

When you want to render out camera with the Cameraide setting you have to use the render buttons provided in the extension. 
Standard rendering operators will use standard render and output settings.

## Tips & Tricks

- Use the frame range sync feature to quickly preview camera-specific animations
- Take advantage of the resolution swap button for quick aspect ratio changes
- Enable "Include Camera Name" in filenames if you want to have them as prefix
- Use the viewport renderer for quick previews and the normal renderer for final output
- Enable "Ignore Markers" to temporarily hide timeline markers during rendering

## Known Issues

- Frame range sync may need to be re-enabled after changing scenes
- Some settings may not update in real-time in all Blender workspace layouts

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License
This addon is licensed under the GNU General Public License version 3 (GPLv3).
For more information, see the LICENSE file or visit https://www.gnu.org/licenses/gpl-3.0.en.html.

## Credits

longiy bullied bunch of AI chabots
