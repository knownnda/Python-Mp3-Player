<p align="center">
  <a href="#how-to-run-it"><b>How to install and run</b></a> ·
  <a href="#features">Features</a> ·
  <a href="#limitations--things-i-want-to-fix">Limitations</a>
</p>

<h1 align="center">Python MP3 Player</h1>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-18181b?style=for-the-badge&logo=python&logoColor=3776AB" alt="Python">
  </a>
</p>

A desktop MP3 player I built in Python. It has a dark-themed window, a playlist, a seek bar, volume control, shuffle and repeat, and it remembers your playlist between sessions.

After building a C++ port scanner, I wanted to try something more visual and interactive, so I made this Python GUI player to learn how GUIs, audio, and program state fit together. It's not perfect [See Limitations](#limitations--things-i-want-to-fix), but it works and I'm proud of it.

<img width="341" height="455" alt="screenshot" src="https://github.com/user-attachments/assets/0d2c2430-a203-4d17-8a03-5cdd9e31f8dd" />  

## Features

- Play, pause, stop, next and previous
- Seek bar you can click or drag, with a live `elapsed / total` timer
- Volume slider
- Shuffle and Repeat all
- Add individual files or a whole folder (it searches subfolders too)
- Remove songs or clear the playlist
- Double-click a song to play it
- Playlist is saved when you close the app and loaded next time (missing files are skipped)
- Keyboard shortcuts: `Space` = play/pause, `←` / `→` = previous / next
- Friendly error messages instead of crashes if a file is missing or broken

## Requirements

- Python 3.8 or newer
- [pygame](https://www.pygame.org/) (plays the audio)
- [mutagen](https://mutagen.readthedocs.io/) (optional, gives more accurate song lengths)
- tkinter (the window). It comes with Python on Windows and macOS. On some Linux installs you need to add it yourself:

```bash
sudo apt install python3-tk
```

## How to run it

1. **Clone the repo**
   ```bash
   git clone https://github.com/knownnda/Python-Mp3-Player.git
   cd Python-Mp3-Player
   ```
2. **Install the libraries**
   ```bash
   pip install -r requirements.txt
   ```
   (If `pip` isn't found, try `python -m pip install -r requirements.txt` or `pip3`.)
3. **Start the player**
   ```bash
   python mp3_player.py
   ```
4. Click **Add files** or **Add folder**, pick some MP3s, then double-click a song or press **Play**.

> Tested on: Windows 11, Python 3.12

## How it works (short version)

Everything is in one file, `mp3_player.py`, split into sections:

| Section | What it does |
| --- | --- |
| Helper functions | Formats time, gets song names and lengths, redraws the playlist |
| Playlist functions | Add, remove, clear, save and load songs |
| Playback functions | Play, pause, stop, next, previous, seek, volume |
| Main loop and window | Builds the tkinter window and runs `update_loop()` every 250 ms |

The window uses **tkinter**. Playing sound uses **pygame.mixer.music**. A function called `update_loop()` runs every quarter of a second using `root.after()`. It updates the timer and seek bar and checks whether the song has finished so it can move on to the next one.

## What this project taught me

- **GUIs are event-driven.** My code doesn't run top to bottom and finish. I set things up, then `mainloop()` waits for clicks and key presses and calls my functions. That took a while to click.
- **You can't use `time.sleep()` in a GUI.** It freezes the whole window. `root.after()` is the right way to do something repeatedly.
- **Keeping track of state is the hard part.** Variables like `current`, `is_playing`, and `is_paused` all have to agree with each other. Most of my bugs were these getting out of sync, for example after removing the song that was playing.
- **Off-by-one errors are real.** Wrapping from the last song to the first (and the other way) and shifting the current index after removing a song made me think carefully about list indexes.
- **Libraries have quirks you only find in the docs.** `pygame` restarts its position counter to 0 every time you seek, so I had to store a `start_offset` and add it back on.
- **Handle the unhappy path.** Files get moved or deleted, and some MP3s are broken. Using `try/except` and checking `os.path.exists()` stopped the app from crashing.
- **Saving data with JSON.** I used `json.dump` and `json.load` to save and restore the playlist, and I learned to ignore a corrupt save file instead of crashing.
- **Optional dependencies.** `try: import mutagen ... except ImportError` lets the program work with or without it.
- **Testing without the GUI.** I tested my playlist and playback logic by swapping the real `pygame` and `tkinter` for fake stand-ins. That showed me how useful it is to keep logic separate from the interface.

## Limitations / things I want to fix

I know about these and plan to improve them as I learn more:

- [ ] **Global variables everywhere.** The state (`playlist`, `current`, `is_playing`, ...) is stored in globals. It works, but it gets messy. I want to rewrite this as a `Player` class (and learn about OOP properly).
- [ ] **One big file.** Splitting it into modules (audio, playlist, GUI) would be cleaner and easier to test.
- [ ] **No automated tests.** I only tested the logic with throwaway scripts. I want to learn `unittest` or `pytest` and add real tests.
- [ ] **Seeking isn't perfectly accurate.** `pygame` can be a little off when seeking in some MP3s, especially variable-bitrate ones. Clicking the seek bar also moves in steps on some systems instead of jumping to the spot.
- [ ] **Slow song-length fallback.** Without `mutagen`, I load the whole file into memory just to get its length. That's slow for big files.
- [ ] **Checking for the end of a song by polling.** I check every 250 ms whether the music has stopped. `pygame` has an end-of-song event that I should use instead.
- [ ] **MP3 only.** `pygame` can also play WAV and OGG, but I only allow `.mp3` for now.
- [ ] **No song info.** It shows the file name only. I'd like to read ID3 tags (title, artist, album) and show album art.
- [ ] **Shuffle is basic.** It picks a random song each time, so the same song can come up again before others have played. A proper shuffled queue would be better.
- [ ] **A broken file stops playback.** It should skip to the next song instead.
- [ ] **Big folders can freeze the window.** Scanning a huge folder happens on the main thread. I need to learn about threads.
- [ ] **Can't reorder songs.** Drag and drop reordering would be nice.
- [ ] **Only one saved playlist.** No named playlists yet.
- [ ] **Button colours on macOS.** tkinter ignores button background colours on macOS, so the buttons look different there. Switching to `ttk` styling or a different GUI toolkit might fix that.

## Project files

```
mp3_player.py      the whole player
requirements.txt   libraries to install
.gitignore         keeps my personal playlist.json out of the repo
README.md          this file
```

## Author

**Naeem Ahmed** ([@knownnda](https://github.com/knownnda))

Feedback and suggestions are welcome. I'm still learning!
