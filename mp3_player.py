# -----------------------------------------------------------
# MP3 Player
# Author: Naeem Ahmed (knownnda)
#
# A desktop MP3 player made with Python.
#   - tkinter  -> the window and buttons (comes with Python)
#   - pygame   -> actually plays the sound
#   - mutagen  -> optional, gets the exact song length
#
# Run it with:  python mp3_player.py
# -----------------------------------------------------------

import os
import json
import random
import tkinter as tk
from tkinter import filedialog, messagebox

import pygame

# mutagen is optional. If it is installed we use it to get the song
# length (more accurate). If not, we fall back to pygame.
try:
    from mutagen.mp3 import MP3
    HAVE_MUTAGEN = True
except ImportError:
    HAVE_MUTAGEN = False

# ---------- colours (dark theme) ----------
BG = "#121212"
PANEL = "#1e1e1e"
FG = "#f1f1f1"
MUTED = "#9a9a9a"
ACCENT = "#1db954"

# The playlist is saved next to this file so it comes back next time
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "playlist.json")

# ---------- program state ----------
# I used global variables to keep track of things. It works, but a
# class would be tidier (see "Limitations" in the README).
playlist = []        # list of file paths
current = -1         # index of the song we are on (-1 = nothing yet)
song_length = 0      # length of the current song in seconds
start_offset = 0     # where in the song we started playing (used for seeking)
is_playing = False
is_paused = False
dragging = False     # True while the user is dragging the seek bar

# ---------- widgets (created in build_gui) ----------
root = None
listbox = None
seek_scale = None
volume_scale = None
title_var = None
time_var = None
status_var = None
play_button = None
shuffle_var = None
repeat_var = None


# ===========================================================
# Helper functions
# ===========================================================

def format_time(seconds):
    """Turn 125 seconds into '2:05'."""
    seconds = int(max(0, seconds))
    return str(seconds // 60) + ":" + str(seconds % 60).zfill(2)


def song_name(path):
    """Get a nice name from a file path (no folder, no .mp3)."""
    return os.path.splitext(os.path.basename(path))[0]


def get_song_length(path):
    """Return the length of an mp3 in seconds (0 if we can't tell)."""
    if HAVE_MUTAGEN:
        try:
            return MP3(path).info.length
        except Exception:
            pass  # fall through to the pygame way
    try:
        # This loads the whole file into memory so it's a bit slow,
        # but it works without any extra libraries.
        return pygame.mixer.Sound(path).get_length()
    except pygame.error:
        return 0


def get_position():
    """How many seconds into the song are we right now?"""
    ms = pygame.mixer.music.get_pos()  # time played since play() was called
    if ms < 0:
        ms = 0
    # get_pos() restarts from 0 every time we seek, so add the offset
    return start_offset + ms / 1000


def refresh_listbox():
    """Redraw the playlist on screen."""
    listbox.delete(0, tk.END)
    for i, path in enumerate(playlist):
        marker = "> " if i == current else "   "
        listbox.insert(tk.END, marker + song_name(path))
    if 0 <= current < len(playlist):
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(current)
        listbox.see(current)


# ===========================================================
# Playlist functions
# ===========================================================

def add_paths(paths):
    """Add mp3 files to the playlist (skips duplicates and non-mp3s)."""
    global current
    added = 0
    for path in paths:
        if path.lower().endswith(".mp3") and path not in playlist:
            playlist.append(path)
            added += 1
    if current == -1 and len(playlist) > 0:
        current = 0
        title_var.set(song_name(playlist[0]))
    refresh_listbox()
    status_var.set("Added " + str(added) + " song(s) - " + str(len(playlist)) + " in playlist")


def add_files():
    files = filedialog.askopenfilenames(
        title="Choose MP3 files",
        filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")])
    add_paths(files)


def add_folder():
    folder = filedialog.askdirectory(title="Choose a folder")
    if not folder:
        return
    found = []
    for folder_path, subfolders, files in os.walk(folder):
        for name in sorted(files):
            if name.lower().endswith(".mp3"):
                found.append(os.path.join(folder_path, name))
    add_paths(found)


def remove_selected():
    global current
    selection = listbox.curselection()
    if not selection:
        return
    i = selection[0]
    del playlist[i]
    if i == current:
        # we removed the song that was playing
        stop_song()
        current = min(i, len(playlist) - 1)  # becomes -1 if playlist is empty
        if current >= 0:
            title_var.set(song_name(playlist[current]))
        else:
            title_var.set("No song loaded")
    elif i < current:
        current -= 1  # everything after i moved up one place
    refresh_listbox()


def clear_playlist():
    global current
    stop_song()
    playlist.clear()
    current = -1
    title_var.set("No song loaded")
    status_var.set("Playlist cleared")
    refresh_listbox()


def save_playlist():
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(playlist, f)
    except OSError:
        pass  # not a big deal if saving fails


def load_playlist():
    if not os.path.exists(SAVE_FILE):
        return
    try:
        with open(SAVE_FILE, "r") as f:
            saved = json.load(f)
    except (OSError, ValueError):
        return
    # only keep files that still exist
    add_paths([p for p in saved if isinstance(p, str) and os.path.exists(p)])
    status_var.set("Loaded " + str(len(playlist)) + " song(s) from last time")


# ===========================================================
# Playback functions
# ===========================================================

def play_song(index, start=0):
    """Start playing playlist[index], optionally from `start` seconds."""
    global current, song_length, start_offset, is_playing, is_paused
    if index < 0 or index >= len(playlist):
        return
    path = playlist[index]

    if not os.path.exists(path):
        pygame.mixer.music.stop()
        is_playing = False
        play_button.config(text="Play")
        status_var.set("File not found: " + song_name(path))
        return

    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(start=start)
    except pygame.error as error:
        pygame.mixer.music.stop()
        is_playing = False
        play_button.config(text="Play")
        status_var.set("Can't play that file: " + str(error))
        return

    current = index
    song_length = get_song_length(path)
    start_offset = start
    is_playing = True
    is_paused = False

    play_button.config(text="Pause")
    title_var.set(song_name(path))
    status_var.set("Song " + str(index + 1) + " of " + str(len(playlist)))
    seek_scale.config(to=max(song_length, 1))
    refresh_listbox()


def play_pause():
    global is_paused
    if len(playlist) == 0:
        return
    if not is_playing:
        play_song(current if current >= 0 else 0)
    elif is_paused:
        pygame.mixer.music.unpause()
        is_paused = False
        play_button.config(text="Pause")
    else:
        pygame.mixer.music.pause()
        is_paused = True
        play_button.config(text="Play")


def stop_song():
    global is_playing, is_paused, start_offset
    pygame.mixer.music.stop()
    is_playing = False
    is_paused = False
    start_offset = 0
    play_button.config(text="Play")
    seek_scale.set(0)
    time_var.set("0:00 / " + format_time(song_length))


def next_song():
    if len(playlist) == 0:
        return
    if shuffle_var.get() and len(playlist) > 1:
        new_index = current
        while new_index == current:  # pick a different song
            new_index = random.randrange(len(playlist))
    else:
        new_index = current + 1
        if new_index >= len(playlist):
            new_index = 0  # wrap back to the start
    play_song(new_index)


def prev_song():
    if len(playlist) == 0:
        return
    # like most players: if we're more than 3 seconds in, restart the song
    if is_playing and get_position() > 3:
        play_song(current)
        return
    new_index = current - 1
    if new_index < 0:
        new_index = len(playlist) - 1  # wrap to the end
    play_song(new_index)


def song_finished():
    """Called when a song ends by itself."""
    at_end = (current == len(playlist) - 1)
    if repeat_var.get() or shuffle_var.get() or not at_end:
        next_song()
    else:
        stop_song()
        status_var.set("Reached the end of the playlist")


def play_selected(event=None):
    """Double-click a song in the list to play it."""
    selection = listbox.curselection()
    if selection:
        play_song(selection[0])


def set_volume(value):
    # the Scale gives us 0-100 but pygame wants 0.0-1.0
    pygame.mixer.music.set_volume(float(value) / 100)


# ---------- seek bar ----------

def seek_pressed(event):
    global dragging
    dragging = True


def seek_released(event):
    global dragging, start_offset
    dragging = False
    if not is_playing:
        return
    target = seek_scale.get()
    if target > song_length - 0.5:
        target = max(song_length - 0.5, 0)
    pygame.mixer.music.play(start=target)
    start_offset = target
    if is_paused:
        pygame.mixer.music.pause()


# ---------- keyboard ----------

def space_pressed(event):
    play_pause()
    return "break"  # stops tkinter from also handling the key


# ===========================================================
# Main loop and window
# ===========================================================

def update_loop():
    """Runs every 250ms to update the time/seek bar and notice when a song ends."""
    if is_playing and not is_paused:
        if pygame.mixer.music.get_busy():
            position = get_position()
            time_var.set(format_time(position) + " / " + format_time(song_length))
            if not dragging:
                seek_scale.set(position)
        else:
            song_finished()
    root.after(250, update_loop)


def on_close():
    pygame.mixer.music.stop()
    save_playlist()
    root.destroy()


def make_button(parent, text, command, width=8):
    return tk.Button(parent, text=text, command=command, width=width,
                     bg=PANEL, fg=FG, activebackground=ACCENT,
                     activeforeground="white", relief="flat", takefocus=0)


def build_gui():
    global root, listbox, seek_scale, volume_scale
    global title_var, time_var, status_var, play_button
    global shuffle_var, repeat_var

    root = tk.Tk()
    root.title("MP3 Player")
    root.geometry("460x580")
    root.minsize(400, 500)
    root.configure(bg=BG)

    title_var = tk.StringVar(value="No song loaded")
    time_var = tk.StringVar(value="0:00 / 0:00")
    status_var = tk.StringVar(value="Add some MP3s to get started")
    shuffle_var = tk.BooleanVar(value=False)
    repeat_var = tk.BooleanVar(value=False)

    # --- now playing ---
    tk.Label(root, textvariable=title_var, bg=BG, fg=FG,
             font=("Arial", 14, "bold"), wraplength=420).pack(pady=(18, 2))
    tk.Label(root, textvariable=status_var, bg=BG, fg=MUTED,
             font=("Arial", 9)).pack()

    # --- seek bar + time ---
    seek_scale = tk.Scale(root, from_=0, to=100, orient="horizontal",
                          showvalue=0, bg=BG, fg=FG, troughcolor=PANEL,
                          highlightthickness=0, activebackground=ACCENT)
    seek_scale.pack(fill="x", padx=20, pady=(14, 0))
    seek_scale.bind("<ButtonPress-1>", seek_pressed)
    seek_scale.bind("<ButtonRelease-1>", seek_released)
    tk.Label(root, textvariable=time_var, bg=BG, fg=MUTED).pack()

    # --- buttons ---
    controls = tk.Frame(root, bg=BG)
    controls.pack(pady=10)
    make_button(controls, "<<", prev_song, 5).pack(side="left", padx=4)
    play_button = make_button(controls, "Play", play_pause, 9)
    play_button.pack(side="left", padx=4)
    make_button(controls, "Stop", stop_song, 5).pack(side="left", padx=4)
    make_button(controls, ">>", next_song, 5).pack(side="left", padx=4)

    # --- volume + shuffle/repeat ---
    options = tk.Frame(root, bg=BG)
    options.pack(fill="x", padx=20)
    tk.Label(options, text="Volume", bg=BG, fg=MUTED).pack(side="left")
    volume_scale = tk.Scale(options, from_=0, to=100, orient="horizontal",
                            showvalue=0, command=set_volume, bg=BG, fg=FG,
                            troughcolor=PANEL, highlightthickness=0,
                            activebackground=ACCENT, length=140)
    volume_scale.pack(side="left", padx=8)
    for text, var in (("Shuffle", shuffle_var), ("Repeat all", repeat_var)):
        tk.Checkbutton(options, text=text, variable=var, bg=BG, fg=FG,
                       selectcolor=PANEL, activebackground=BG,
                       activeforeground=FG, takefocus=0).pack(side="left", padx=4)
    volume_scale.set(70)

    # --- playlist ---
    list_frame = tk.Frame(root, bg=BG)
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)
    scrollbar = tk.Scrollbar(list_frame)
    listbox = tk.Listbox(list_frame, bg=PANEL, fg=FG, selectbackground=ACCENT,
                         selectforeground="white", highlightthickness=0,
                         borderwidth=0, activestyle="none",
                         yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    listbox.bind("<Double-Button-1>", play_selected)
    listbox.bind("<Return>", play_selected)
    listbox.bind("<space>", space_pressed)

    # --- playlist buttons ---
    bottom = tk.Frame(root, bg=BG)
    bottom.pack(pady=(0, 14))
    make_button(bottom, "Add files", add_files, 10).pack(side="left", padx=3)
    make_button(bottom, "Add folder", add_folder, 10).pack(side="left", padx=3)
    make_button(bottom, "Remove", remove_selected, 8).pack(side="left", padx=3)
    make_button(bottom, "Clear", clear_playlist, 8).pack(side="left", padx=3)

    # --- keyboard shortcuts ---
    root.bind("<space>", space_pressed)
    root.bind("<Right>", lambda event: next_song())
    root.bind("<Left>", lambda event: prev_song())

    root.protocol("WM_DELETE_WINDOW", on_close)


def main():
    try:
        pygame.mixer.init()
    except pygame.error as error:
        print("Could not start the audio system:", error)
        return
    build_gui()
    load_playlist()
    update_loop()
    root.mainloop()


if __name__ == "__main__":
    main()
