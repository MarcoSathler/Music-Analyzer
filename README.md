# 📦 Music Analyzer - Project Overview

## 🎯 What is this?
A professional Python tool to automatically **analyze**, **rename**, and **organize** music libraries.
Focuses on **BPM** and **Key**, essential for DJs and producers.

---

## ✨ Key Features

| Feature | Description | Technology |
| :--- | :--- | :--- |
| **Accurate BPM** | Detects tempo and rounds intelligently (decimals > 0.1 round up). | `Librosa` |
| **Native Key** | Detects musical key without external apps. | `Krumhansl-Schmuckler` |
| **Renaming** | Standardizes: `[Key] - [BPM] BPM - [Name]`. | `Python OS/Pathlib` |
| **Name Cleaning** | Removes "junk" (e.g., Official Video) and replaces chars. | `Regex` |
| **Flexible Notation** | Supports Classic (`Cm`) and Camelot (`8A`). | Smart Mapping |
| **Metadata** | Updates the file's "Title" tag. | `Mutagen` |
| **Reports** | Generates full analysis CSV. | `CSV` |
| **Unified GUI** | All options in a single simple window. | `Tkinter` |

---

## 🛠️ Installation & Usage

### Dependencies
Only standard Python libraries:
```bash
pip install librosa numpy mutagen
```

### Execution
Run the main script:
```bash
python music_analyzer.py
```

---

## 🚀 Version Highlights

1. **Zero External Dependencies**: No more KeyFinder or PyMusicKit. Runs natively.
2. **Improved Interface**: Single configuration screen replaces multiple popups.
3. **Key Conversion**: Automatically converts old notations (Cm -> 8A).
4. **Safety**: Checks for existing data to prevent duplicate naming.

---

*Optimized for Windows, compatible with Linux and macOS.*

# 🚀 GET STARTED - Quick Guide

## ⚡ In 30 Seconds

### 1. Open Terminal/Prompt
**Windows:**
```powershell
Win + R -> type 'cmd' -> Enter
```

### 2. Navigate to Project Folder
```bash
cd "C:\Path\To\MusicAnalyzerNew"
```

### 3. Install Dependencies (Once)
```bash
pip install librosa numpy mutagen
```

### 4. Run the Program
```bash
python music_analyzer.py
```

### 5. Done!
1. **Select** your music folder.
2. In the **Analysis Configuration** window, choose your preferences:
   - **Rename Files**: Yes/No
   - **Notation**: Classic (Cm) or Camelot (8A)
   - **Remove Text**: Clean unwanted text (e.g., "Official Video")
3. Click **OK** and watch the magic happen! ✨

---

## 🔧 Troubleshooting

### Error: "Module not found"
If you see missing module errors, run:
```bash
pip install librosa numpy mutagen
```

### Error: "ffmpeg not found"
`librosa` requires FFMPEG to read audio files.
- **Windows**: Download FFMPEG and add it to your system PATH.

---

## 📂 What does this script do?
1. **Analyzes BPM**: Detects tempo and rounds intelligently.
2. **Analyzes Key**: Uses native Krumhansl-Schmuckler algorithm (highly accurate).
3. **Renames**: Standardizes filenames (e.g., `8A - 128 BPM - My Song.mp3`).
4. **Updates Tags**: Updates the 'Title' metadata of the file.
5. **Generates Report**: Creates a detailed CSV in the analyzed folder.

---

**Version:** 2026.1 (Native)
**Author:** Marco Sathler

# 🎵 Renaming Guide (Music Analyzer)

The script features an intelligent renaming system to keep your library organized and clean.

---

## ✨ New Filename Pattern

When you enable **"Rename Files"**, your music files will be renamed to:

```
[Key] - [BPM] BPM - [Clean Name]
```

### Examples:
- `8A - 128 BPM - My Song.mp3` (Camelot Notation)
- `Cm - 128 BPM - My Song.mp3` (Classic Notation)

---

## 🚀 Configuration Options

After selecting a folder, a window appears with the following options:

### 1. ☑️ Rename Files
Check this box to enable renaming. If unchecked, the script only analyzes and generates the CSV report.

### 2. 🔘 Key Notation
Choose how the key should appear in the filename:
- **Classic**: `Cm`, `F#`, `Abm`
- **Camelot (Alphanumeric)**: `8A`, `2B`, `4A` (Ideal for DJs - Camelot Wheel)

**Smart Conversion:**
If a file already has a key in the name but in the wrong format (e.g., has "Cm" but you chose "Camelot"), the script automatically **replaces** "Cm" with "8A".

### 3. ✂️ Remove Text
Enter words or phrases you want to delete from the original filename. Separate by comma.
*Example:* `Official Video, [HD], (Lyrics)`
*Result:* `Song Name [HD].mp3` -> `Song Name.mp3`

### 4. 🔁 Replace Characters
Swap specific characters. Use the format `old:new`.
*Example:* `_: ` (Replaces underscore with space)
*Result:* `Song_Name.mp3` -> `Song Name.mp3`

---

## 🛡️ Safety & Intelligence

1. **Anti-Duplication**: The script won't add BPM or Key if they are already present in the correct format.
2. **Metadata Backup**: The original filename is saved in the CSV report.
3. **Tags**: The new filename is automatically written to the "Title" metadata tag.
4. **Extension Preserved**: .mp3 remains .mp3, etc.

---

## 📋 Report
A `.csv` file is generated in the analyzed folder detailing the "Before and After" of every track.


