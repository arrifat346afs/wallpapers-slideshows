#!/usr/bin/env python3
import os
import sys
import random
import subprocess
import json
import time

# ✅ Set your wallpaper directory here
WALLPAPER_DIR = "/home/rifat/Pictures/wallpaper/"

# Path to your wallpaper switching script
WALL_SCRIPT = "/home/rifat/.config/quickshell/ii/scripts/colors/switchwall.sh"

# File to keep track of already used wallpapers
HISTORY_FILE = os.path.expanduser("~/.cache/wallpaper_history.json")

# Interval in seconds (e.g., 300 = 5 minutes)
INTERVAL = 300  

# File to store the path of the current wallpaper
CURRENT_WALLPAPER_FILE = os.path.expanduser("~/.cache/current_wallpaper.txt")  

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {"used": []}

def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

def get_wallpapers(directory):
    exts = (".jpg", ".jpeg", ".png")
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(exts)]

def set_random_wallpaper():
    wallpapers = get_wallpapers(WALLPAPER_DIR)
    if not wallpapers:
        print("❌ No wallpapers found.")
        return None

    history = load_history()
    used = set(history.get("used", []))

    # Reset history if all wallpapers are used
    available = [w for w in wallpapers if w not in used]
    if not available:
        print("✅ All wallpapers used, resetting history...")
        used.clear()
        available = wallpapers

    # Pick a random wallpaper
    chosen = random.choice(available)

    # --- Write to state file FIRST for robustness ---
    try:
        print(f"LOG: Writing '{chosen}' to state file: {CURRENT_WALLPAPER_FILE}")
        with open(CURRENT_WALLPAPER_FILE, "w") as f:
            f.write(chosen)
        print("LOG: Successfully wrote to state file.")
    except Exception as e:
        print(f"!!! ERROR: Failed to write to state file: {e}")
    # ------------------------------------------------

    print(f"🎨 Setting wallpaper: {chosen}")

    # Call your switchwall.sh script
    subprocess.run([WALL_SCRIPT, chosen])

    # Save history
    used.add(chosen)
    history["used"] = list(used)
    save_history(history)

    return chosen

def main():
    if len(sys.argv) > 1:
        handle_command(sys.argv[1])
    else:
        print(f"🖼 Wallpaper slideshow started — changing every {INTERVAL} seconds.")
        # Ensure pause file doesn't exist from a previous run
        if os.path.exists(PAUSE_FILE):
            os.remove(PAUSE_FILE)
        while True:
            if not os.path.exists(PAUSE_FILE):
                set_random_wallpaper()
            time.sleep(INTERVAL)

PAUSE_FILE = os.path.expanduser("~/.cache/slideshow.paused")

def handle_command(command):
    if command == "next":
        set_random_wallpaper()
    elif command == "previous":
        # With the current history implementation, "previous" is the same as "next"
        print("Setting another random wallpaper for 'previous' command.")
        set_random_wallpaper()
    elif command == "pause":
        if os.path.exists(PAUSE_FILE):
            os.remove(PAUSE_FILE)
            print("▶️ Resumed slideshow.")
        else:
            with open(PAUSE_FILE, "w") as f:
                f.write("")
            print("⏸ Paused slideshow.")
    elif command == "current":
        if os.path.exists(CURRENT_WALLPAPER_FILE):
            with open(CURRENT_WALLPAPER_FILE, "r") as f:
                # Print in the same format as a normal change for consistency
                print(f"🎨 Setting wallpaper: {f.read().strip()}")
    else:
        print(f"❓ Unknown command: {command}")

if __name__ == "__main__":
    main()

