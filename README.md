# DaVinci Resolve: Subtitle to Text+ Converter (Cut-to-Cut)

A high-performance Python script for **DaVinci Resolve Studio** (compatible with versions 18.5, 19, 20, and 21+) that converts an entire Subtitle track into frame-accurate, cut-to-cut **Text+ (Fusion Title)** clips on a designated Video track.

---

## ⚡ What It Does
- **Frame-Accurate Cut-to-Cut**: Every Text+ clip matches the exact `Start Frame`, `End Frame`, and `Duration` of the corresponding subtitle item.
- **Batch Processing**: Converts hundreds of subtitles (e.g. 500+ captions) in ~10–12 seconds.
- **Full Fusion Control**: Unlocks all advanced Fusion title capabilities (drop shadows, stroke/outlines, custom fonts, animations, keyframing, and motion graphics) that standard closed-caption subtitle tracks do not support.
- **Custom Template Support**: If you style a Text+ title in your Media Pool and name it `TextPlus` or `SubtitleTemplate`, every single cut clip will automatically inherit your custom font, size, shadows, and animations.
- **Non-Destructive**: Never overwrites existing video tracks—automatically detects empty tracks or creates a dedicated `Subtitles Text+` track.

---

## 🚀 How to Run

### Method 1: Directly Inside DaVinci Resolve (Recommended)
The script has been installed directly into your DaVinci Resolve scripts menu:
1. Open your project in **DaVinci Resolve Studio**.
2. Go to the top menu bar:  
   **Workspace** ➔ **Scripts** ➔ **Edit** ➔ **Convert_Subtitle_To_TextPlus**
3. The script will automatically process your active timeline and convert the subtitle track to Video 2.

### Method 2: From the Terminal / Command Line
Run the script anytime via macOS terminal:
```bash
/usr/bin/python3 "/Users/auxalus/Desktop/projects/davinciassetsnew/Convert_Subtitle_To_TextPlus.py"
```

### Method 3: From the DaVinci Resolve Console
1. In DaVinci Resolve, go to **Workspace** ➔ **Console**.
2. Switch the console language to **Py3**.
3. Run the script file or execute the function directly.

---

## 🎨 Customizing Styles & Templates

### Option A: Use a Custom Media Pool Template
1. In DaVinci Resolve's Edit page, open the **Effects** panel (top-left) ➔ **Titles** ➔ **Text+**.
2. Drag a **Text+** title into your **Media Pool** root bin.
3. Name it **`SubtitleTemplate`** or **`TextPlus`**.
4. Double-click it or open the **Inspector** and customize your preferred font, size, tracking, outlines, shadows, or Fusion animations.
5. Run the script! Every cut-to-cut clip will inherit your styling.

### Option B: Quick Settings in the Script
Open `Convert_Subtitle_To_TextPlus.py` and modify the top configuration section:
```python
CUSTOM_FONT = "Montserrat"   # e.g., "Arial", "Open Sans", "Impact" (or None for template font)
CUSTOM_SIZE = 0.08           # e.g., 0.07, 0.08 (or None for template size)
CLIP_COLOR = "Teal"          # Timeline clip color ("Teal", "Orange", "Yellow", "Blue", etc.)
SUBTITLE_TRACK_INDEX = 1     # Which subtitle track to read
```

---

## 📁 File Locations
- **Workspace Script**: `/Users/auxalus/Desktop/projects/davinciassetsnew/Convert_Subtitle_To_TextPlus.py`
- **DaVinci Resolve Installed Script**: `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Edit/Convert_Subtitle_To_TextPlus.py`
- **Template Bin**: `/Users/auxalus/Desktop/projects/davinciassetsnew/templates/__RS_TextPlus_FPS__.drb`

# davinciresolve-scripts
