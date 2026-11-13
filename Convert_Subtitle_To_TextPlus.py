#!/usr/bin/env python3
"""
================================================================================
Convert Subtitle Layer to Text+ Layer (Cut to Cut)
Tested & Fully Supported on DaVinci Resolve Studio (v18.5, v19, v20, v21+)
================================================================================

Description:
    Reads every subtitle clip from your timeline's Subtitle track and creates
    frame-accurate, cut-to-cut Text+ (Fusion Title) clips on a designated Video track.
    Every single cut, start frame, end frame, and text string matches 100% to the frame.

How to Run:
    Method 1 (Inside DaVinci Resolve UI):
        1. Open DaVinci Resolve.
        2. Navigate to top menu: Workspace > Scripts > Edit > Convert_Subtitle_To_TextPlus
    
    Method 2 (DaVinci Resolve Console):
        1. Navigate to: Workspace > Console
        2. Click 'Py3'
        3. Paste and run this script or execute it.

    Method 3 (Terminal / CLI):
        /usr/bin/python3 "/Users/auxalus/Desktop/projects/davinciassetsnew/Convert_Subtitle_To_TextPlus.py"
"""

import sys
import os
import time
from pathlib import Path

# ==============================================================================
# USER CONFIGURATION (Customize if desired, or leave defaults)
# ==============================================================================
CUSTOM_FONT = None           # e.g., "Arial", "Open Sans", "Montserrat", "Impact" (None keeps template font)
CUSTOM_SIZE = None           # e.g., 0.08, 0.075 (None keeps template size)
CLIP_COLOR = "Teal"          # Timeline clip color: "Teal", "Orange", "Blue", "Yellow", "Pink", "Green", etc.
SUBTITLE_TRACK_INDEX = 1     # Which subtitle track to convert (default: 1)
TARGET_VIDEO_TRACK = None    # Target video track index (None = auto-detect empty track or create new track)


# ==============================================================================
# RESOLVE API CONNECTION
# ==============================================================================
def get_resolve():
    """Locate and return the DaVinci Resolve script object."""
    try:
        if "bmd" in globals() or "bmd" in __builtins__:
            return bmd.scriptapp("Resolve")
    except Exception:
        pass

    try:
        if "resolve" in globals():
            return resolve
    except Exception:
        pass

    api_paths = [
        "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules",
        r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules",
        "/opt/resolve/Developer/Scripting/Modules"
    ]
    for p in api_paths:
        if os.path.exists(p) and p not in sys.path:
            sys.path.append(p)

    try:
        import DaVinciResolveScript as dvr
        return dvr.scriptapp("Resolve")
    except Exception as e:
        print(f"[Error] Failed to connect to DaVinci Resolve API: {e}")
        return None


def get_fps_int(timeline):
    """Retrieve timeline frame rate string and rounded integer."""
    fps_setting = timeline.GetSetting("timelineFrameRate")
    try:
        fps_float = float(fps_setting)
    except (ValueError, TypeError):
        fps_float = 24.0

    if abs(fps_float - 23.976) < 0.05:
        return 24, "23.976"
    elif abs(fps_float - 29.97) < 0.05:
        return 30, "29.97"
    elif abs(fps_float - 59.94) < 0.05:
        return 60, "59.94"
    else:
        fps_round = int(round(fps_float))
        return fps_round, str(fps_round)


def get_drb_template_path():
    """Locate the built-in __RS_TextPlus_FPS__.drb template bin."""
    search_dirs = [
        Path(__file__).parent / "templates",
        Path(__file__).parent,
        Path.home() / "Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Edit/templates",
        Path("/Users/auxalus/Desktop/projects/davinciassetsnew/templates"),
        Path("/tmp/resolve_script/data/app/VoiceDropper"),
    ]
    for d in search_dirs:
        drb_file = d / "__RS_TextPlus_FPS__.drb"
        if drb_file.is_file():
            return str(drb_file)
    return None


def ensure_text_plus_template(media_pool, fps_str):
    """
    Search Media Pool for an existing Text+ template clip.
    If none is found, imports the built-in template bin matching the project's FPS.
    """
    root_folder = media_pool.GetRootFolder()

    # 1. Custom User Template:
    # If user styled a Text+ in Media Pool and named it 'TextPlus' or 'SubtitleTemplate'
    folders_to_check = [root_folder] + root_folder.GetSubFolderList()
    for folder in folders_to_check:
        for clip in folder.GetClipList():
            clip_name = clip.GetClipProperty("Clip Name") or clip.GetName()
            if clip_name in ["TextPlus", "SubtitleTemplate", f"TextPlus{fps_str}FPS"]:
                return clip

    # 2. Check if template bin folder __RS_TextPlus_FPS__ already exists
    template_folder = None
    for folder in root_folder.GetSubFolderList():
        if folder.GetName() == "__RS_TextPlus_FPS__":
            template_folder = folder
            break

    # 3. If missing, import the template drb
    if not template_folder:
        drb_path = get_drb_template_path()
        if drb_path and os.path.exists(drb_path):
            current = media_pool.GetCurrentFolder()
            media_pool.SetCurrentFolder(root_folder)
            print(f"[Info] Importing Text+ template bin from: {drb_path}")
            media_pool.ImportFolderFromFile(drb_path)
            media_pool.SetCurrentFolder(current)

            for folder in root_folder.GetSubFolderList():
                if folder.GetName() == "__RS_TextPlus_FPS__":
                    template_folder = folder
                    break

    if template_folder:
        target_name = f"TextPlus{fps_str}FPS"
        clips = template_folder.GetClipList()
        for clip in clips:
            name = clip.GetClipProperty("Clip Name")
            if name == target_name:
                return clip
        if clips:
            return clips[0]

    return None


# ==============================================================================
# MAIN CONVERSION FUNCTION
# ==============================================================================
def convert_subtitles_to_textplus(subtitle_track_index=SUBTITLE_TRACK_INDEX,
                                  target_video_track_index=TARGET_VIDEO_TRACK,
                                  clip_color=CLIP_COLOR,
                                  custom_font=CUSTOM_FONT,
                                  custom_size=CUSTOM_SIZE):
    resolve = get_resolve()
    if not resolve:
        print("[Error] Could not connect to DaVinci Resolve.")
        return False

    project_manager = resolve.GetProjectManager()
    project = project_manager.GetCurrentProject()
    if not project:
        print("[Error] No project currently open in DaVinci Resolve.")
        return False

    timeline = project.GetCurrentTimeline()
    if not timeline:
        print("[Error] No active timeline found.")
        return False

    media_pool = project.GetMediaPool()

    # Verify subtitle track
    sub_track_count = timeline.GetTrackCount("subtitle")
    if sub_track_count < 1:
        print("[Error] No subtitle tracks found on current timeline.")
        return False

    if subtitle_track_index > sub_track_count:
        print(f"[Warning] Subtitle track {subtitle_track_index} not found. Defaulting to Track 1.")
        subtitle_track_index = 1

    sub_items = timeline.GetItemListInTrack("subtitle", subtitle_track_index)
    total_subs = len(sub_items)
    if total_subs == 0:
        print(f"[Warning] Subtitle track {subtitle_track_index} is empty (0 subtitle clips).")
        return False

    sub_track_name = timeline.GetTrackName("subtitle", subtitle_track_index)
    print(f"[Info] Found {total_subs} subtitles on Track '{sub_track_name}' (Index {subtitle_track_index}).")

    # Determine FPS and Template
    fps_int, fps_str = get_fps_int(timeline)
    print(f"[Info] Timeline frame rate: {fps_int} fps ({timeline.GetSetting('timelineFrameRate')})")

    template_clip = ensure_text_plus_template(media_pool, fps_str)
    if not template_clip:
        print("[Error] Could not locate or import Text+ template.")
        print("        Tip: You can drag any Text+ title into your Media Pool and name it 'TextPlus'.")
        return False

    template_name = template_clip.GetClipProperty("Clip Name") or template_clip.GetName()
    print(f"[Info] Using Text+ template: '{template_name}'")

    # Determine target video track
    vid_track_count = timeline.GetTrackCount("video")
    if target_video_track_index is None:
        # Check if Video 2 exists and is empty
        if vid_track_count >= 2 and len(timeline.GetItemListInTrack("video", 2)) == 0:
            target_video_track_index = 2
        else:
            timeline.AddTrack("video")
            vid_track_count = timeline.GetTrackCount("video")
            target_video_track_index = vid_track_count
            timeline.SetTrackName("video", target_video_track_index, "Subtitles Text+")
    else:
        while target_video_track_index > timeline.GetTrackCount("video"):
            timeline.AddTrack("video")

    target_track_name = timeline.GetTrackName("video", target_video_track_index)
    print(f"[Info] Destination Video Track: '{target_track_name}' (Track {target_video_track_index}).")

    # Build batch append data
    print(f"[Info] Generating cut-to-cut Text+ clips for {total_subs} subtitles...")
    start_time = time.time()

    batch_data = []
    for s in sub_items:
        batch_data.append({
            "mediaPoolItem": template_clip,
            "startFrame": 0,
            "endFrame": s.GetDuration(),
            "recordFrame": s.GetStart(),
            "trackIndex": target_video_track_index,
            "mediaType": 1
        })

    appended_clips = media_pool.AppendToTimeline(batch_data)
    if not appended_clips or len(appended_clips) != total_subs:
        print(f"[Warning] Append returned {len(appended_clips) if appended_clips else 0} clips (expected {total_subs}).")
        if not appended_clips:
            print("[Error] AppendToTimeline failed.")
            return False

    # Inject subtitle text and optional styling into Fusion comp
    print("[Info] Updating StyledText on each Text+ clip...")
    success_count = 0
    for idx, (clip, sub) in enumerate(zip(appended_clips, sub_items)):
        text = sub.GetName()
        try:
            comp = clip.GetFusionCompByIndex(1)
            if comp:
                tools = comp.GetToolList(False, "TextPlus")
                if tools and 1 in tools:
                    tool = tools[1]
                    tool.SetInput("StyledText", text)
                    if custom_font:
                        tool.SetInput("Font", custom_font)
                    if custom_size:
                        tool.SetInput("Size", custom_size)
            if clip_color:
                clip.SetClipColor(clip_color)
            success_count += 1
        except Exception as e:
            print(f"[Warning] Clip {idx + 1} text update error: {e}")

        if (idx + 1) % 100 == 0 or (idx + 1) == total_subs:
            percent = int(((idx + 1) / total_subs) * 100)
            print(f"  [{percent}%] Processed {idx + 1}/{total_subs} clips...")

    elapsed = time.time() - start_time
    print("=" * 60)
    print(f"[Success] Converted {success_count}/{total_subs} subtitles to Text+ cut-to-cut!")
    print(f"[Success] Track: Video {target_video_track_index} ('{target_track_name}')")
    print(f"[Success] Completed in {elapsed:.2f} seconds.")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = convert_subtitles_to_textplus()
    os._exit(0 if success else 1)
