# Cameraide

**Blender addon — version 1.0.8 · requires Blender 4.2+**

Cameraide gives every camera in your scene its own independent render settings. Switch cameras and the output format, resolution, frame range, and file path switch with it — no more manually re-configuring the Output panel between shots.

---

## Installation

1. Download or clone the repository as a folder named `Cameraide`.
2. In Blender: **Edit → Preferences → Add-ons → Install** and select the folder (or the zipped folder).
3. Enable **Cameraide** in the add-on list.
4. The panel appears in the **3D View sidebar** under the **Camera** tab.

---

## Quick Start

1. Open the **Camera** tab in the 3D View sidebar.
2. Click the camera name button at the top of the Cameraide panel to **befriend** it (button highlights).
3. Configure resolution, frame range, output path, and file format for that camera.
4. Select a different camera — the panel updates to show that camera's settings.
5. Press **Snapshot**, **Playblast**, or **All Cameras** to render.

---

## Panel Layout

```
[ CAM_A ]                        ← befriend toggle (active camera)

▶ Cameraide Cameras              ← collapsible list
▶ Other Cameras

▼ Resolution
    Presets ▾
    [ 1920 ] ⇄ [ 1080 ]
    Percentage ████████ 100%

▼ Frame Range
    Mode: Per Camera ▾
    Start [ 1 ]  End [ 250 ]
    Step  [ 1 ]
    [ Sync OFF ]

▼ File Output
    /path/to/output/
    subfolder/
    filename
    ▶ Advanced
        ☐ Overwrite Existing
        ☐ Include Camera Name
        ☐ Burn Metadata

▼ File Format
    [ PNG ][ JPEG ][ EXR ]
    [ MP4 ][ MKV  ][ MOV ]
    ▶ Advanced
        (format-specific settings)

┌────────────────────────────────┐
│ Viewport        Normal         │
│ [ Snapshot ]    [ Snapshot ]   │
│ [ Playblast ]   [ Playblast ]  │
│ [ All Cameras ] [ All Cameras ]│
└────────────────────────────────┘
```

---

## Features

### Camera Management

Each camera independently stores its settings. The **befriend** button at the top of the panel toggles Cameraide on or off for the current camera. The panel displays two collapsible lists — one for cameras with Cameraide enabled and one for the rest — making it easy to see at a glance which cameras are set up and to jump between them.

### Resolution

Resolution X/Y, a swap button, and a percentage scale are stored per camera. A **Presets** menu sits above the inputs for quick access to common resolutions. Whenever you adjust these values the native Blender Output panel updates immediately so the viewport and render settings stay in sync.

### Frame Range

Two modes are available:

- **Per Camera** — explicit start, end, and step fields. An optional **Sync** toggle pushes these values to the scene timeline whenever this camera is active, so the timeline always reflects the current camera's range.
- **Timeline Markers** — Cameraide reads the timeline markers bound to this camera and derives the frame ranges automatically. Useful for multi-shot sequences on a single timeline.

Frame start is clamped to at most `end − 1`; frame end is clamped to at least `start + 1`.

When you befriend a camera, Cameraide auto-detects which mode is appropriate based on whether timeline markers are present, and shows a warning if the current mode conflicts with the scene state.

### File Output

- **Output Path / Subfolder / Filename** — full per-camera control over where renders are saved.
- **Advanced** (collapsible sub-group):
  - **Overwrite Existing** — skip frames already on disk.
  - **Include Camera Name** — append the camera's object name to the filename.
  - **Burn Metadata** — embed render information into image pixels.

### File Format

Six formats are available in two rows of buttons:

| Row | Formats |
|-----|---------|
| Image | PNG · JPEG · EXR |
| Video | MP4 (H.264) · MKV (H.264) · MOV (ProRes) |

Format-specific settings live inside a collapsible **Advanced** sub-group:

| Format | Advanced Settings |
|--------|------------------|
| PNG | Bit depth · Compression · Alpha Transparency |
| JPEG | Quality |
| EXR | Bit depth · Codec · Alpha Transparency |
| MP4 / MKV | Quality (CRF) · Bitrate · GOP Size · Audio Codec + Bitrate |
| MOV (ProRes) | Audio Codec + Bitrate · Alpha Transparency |

**Alpha Transparency** is a per-format flag — enabling it for PNG does not affect EXR or ProRes, and vice versa.

**Audio** is controlled by the codec dropdown. Select *No Audio* to disable audio; select any other codec (MP3 is the default for new cameras) to enable it and reveal the bitrate field.

### Bidirectional Settings Sync

Changes made in Cameraide are pushed to Blender's native Output panel immediately. Changes made directly in the native Output panel are detected via `msgbus` and written back to the active camera's Cameraide settings:

- **Format/codec changes** (native Output → Cameraide) are handled by a dedicated callback subscribed to `ImageFormatSettings` and `FFmpegSettings`.
- **Resolution/transparency changes** (native Output → Cameraide) are handled by a separate callback subscribed to `RenderSettings`.

The two-callback design prevents resolution writes from accidentally triggering a format revert, and a `_syncing_native` guard prevents feedback loops.

### Render Operators

The render panel is always visible at the bottom of the Cameraide panel whenever a camera with custom settings is active. It is split into two columns:

| Left — Viewport | Right — Normal |
|-----------------|----------------|
| Snapshot | Snapshot |
| Playblast | Playblast |
| All Cameras | All Cameras |

- **Snapshot** — renders a single still frame.
- **Playblast** — renders the full animation range for this camera.
- **All Cameras** — batch-renders every Cameraide camera in sequence.

Operators fall back to the **scene camera** when no camera object is explicitly selected, so the buttons are never unexpectedly greyed out.

### Batch Rendering

*All Cameras* builds a queue of `(camera, start_frame, end_frame)` tuples from every Cameraide camera in the scene. Jobs run one at a time — the next job starts only after the current one completes — via Blender's timer system to keep the UI responsive. Cameraide's own camera-switch handler is suspended during batch runs to prevent it from interfering with the sequential camera switching. All native render settings are fully restored after each render via `RenderCleanupManager`.

---

## Location

| Interface | Path |
|-----------|------|
| 3D View sidebar | **Camera** tab → Cameraide panel |
| Camera Properties | **Properties → Camera → Cameraide** |

---

## Compatibility

| Requirement | Version |
|-------------|---------|
| Blender | 4.2 or later |
| Python | bundled with Blender |
| Platform | Windows · macOS · Linux |

---

## License

See repository root for license information.
