<p align="center">
  <a href="#how-to-run-it"><b>How to install and run</b></a> ·
  <a href="#features">Features</a> ·
  <a href="#limitations--things-i-want-to-fix">Limitations</a>
</p>

<h1 align="center"> Python MP3 Player</h1>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-18181b?style=for-the-badge&logo=python&logoColor=3776AB" alt="Python">
  </a>
</p>

A simple desktop MP3 player I made in Python using tkinter and pygame.
It plays your MP3 files, has a playlist, a seek bar, volume control, shuffle and repeat, and it remembers your playlist when you close it.

<p align="center">
  <img width="341" height="455" alt="screenshot" src="https://github.com/user-attachments/assets/0d2c2430-a203-4d17-8a03-5cdd9e31f8dd" />
</p>

## How to run it

You need Python 3.8 or newer. tkinter comes with Python on Windows and macOS. On Linux you may need `sudo apt install python3-tk`.

1. **Clone the repo**
```bash
   git clone https://github.com/knownnda/Python-Mp3-Player.git
   cd Python-Mp3-Player
```
2. **Install the libraries**
```bash
   pip install -r requirements.txt
```
3. **Start the player**
```bash
   python mp3_player.py
```
4. **Play some music**
   Click **Add files** or **Add folder**, pick some MP3s, then double-click a song or press **Play**.

> Tested on: Windows, Python 3.x

## Features

- Play, pause, stop, next and previous
- Seek bar you can click or drag, with a live timer
- Volume slider
- Shuffle and Repeat all
- Add single files or a whole folder
- Remove songs or clear the playlist
- Playlist is saved when you close the app and loaded next time
- Keyboard shortcuts: `Space` = play/pause, `←` / `→` = previous / next
- Error messages instead of crashes if a file is missing or broken

## What do the libraries do?

**tkinter** makes the window, buttons, sliders and playlist box. It comes with Python.

**pygame** plays the actual sound. I only use its `mixer.music` part.

**mutagen** is optional. It reads the exact length of a song. Without it, the program still works but is a bit slower at finding the length.

## How it works

Everything is in one file, `mp3_player.py`. It has four sections:

1. Helper functions (format time, get song names and lengths)
2. Playlist functions (add, remove, clear, save, load)
3. Playback functions (play, pause, stop, next, previous, seek, volume)
4. The window, plus a loop that runs every 250 ms to update the timer and move on to the next song

## What I Learnt

This was my first Python GUI project. It taught me quite a lot about Python, GUIs and how a program keeps track of what is going on.

**Python**
I got more comfortable with functions, lists, loops, `try/except`, and reading and writing files.

**GUIs**
I learnt that a GUI doesn't run top to bottom and finish. I set everything up, then `mainloop()` waits for clicks and key presses and calls my functions. I also learnt that `time.sleep()` freezes the window, so `root.after()` is used to repeat things instead.

**Keeping track of state**
This was the hardest part. Variables like `current`, `is_playing` and `is_paused` all have to agree with each other. Most of my bugs came from them getting out of sync, for example after removing the song that was playing.

**Libraries and their quirks**
`pygame` restarts its position timer from 0 every time you seek, so I had to store a `start_offset` and add it back on. I also learnt to make a library optional with `try: import ... except ImportError`.

**Saving data**
I used JSON (`json.dump` and `json.load`) to save the playlist. I also made the program ignore a broken save file instead of crashing.

**Handling errors**
Files get moved or deleted, and some MP3s are broken. Checking `os.path.exists()` and using `try/except` stopped the program from crashing.

## Limitations / things I want to fix

I know about these and want to improve them as I learn more:

- [ ] **Global variables.** I stored the state in global variables. It works, but a `Player` class would be tidier.
- [ ] **One big file.** I want to split it into separate files for audio, playlist and GUI.
- [ ] **No automated tests.** I want to learn `unittest` or `pytest`.
- [ ] **Seeking isn't perfect.** It can be slightly off on some MP3s, especially variable-bitrate ones.
- [ ] **Checking for the end of a song by polling.** I check every 250 ms. `pygame` has an end-of-song event I should use instead.
- [ ] **MP3 only.** `pygame` can play other formats too.
- [ ] **No song info or album art.** It only shows the file name. I want to read ID3 tags.
- [ ] **Basic shuffle.** It picks a random song each time, so one can repeat before the others have played.
- [ ] **A broken file stops playback.** It should skip to the next song.
- [ ] **Big folders can freeze the window.** I need to learn about threads.
- [ ] **Can't reorder songs** and **only one saved playlist.**
- [ ] **Button colours on macOS.** tkinter ignores button colours there.

## Project files

```
mp3_player.py      the whole player
requirements.txt   libraries to install
.gitignore         keeps my personal playlist.json out of the repo
README.md          this file
```

## Disclaimer

This project is made for educational purposes to help me learn Python and GUI programming.
Please only play MP3s that you legally own or have permission to use. I am not responsible for any misuse of this software.

## Author

**Naeem Ahmed** ([@knownnda](https://github.com/knownnda))

I'm still learning, so feedback is welcome.
