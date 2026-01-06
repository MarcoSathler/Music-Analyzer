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

## 📂 File Structure

- `music_analyzer.py`: **THE BRAIN.** Main script containing all logic.
- `GET_STARTED.md`: Quick setup guide.
- `RENAMING_GUIDE.md`: Details on how renaming works.
- `PROJECT_OVERVIEW.md`: This file.

---

## 🚀 Version Highlights

1. **Zero External Dependencies**: No more KeyFinder or PyMusicKit. Runs natively.
2. **Improved Interface**: Single configuration screen replaces multiple popups.
3. **Key Conversion**: Automatically converts old notations (Cm -> 8A).
4. **Safety**: Checks for existing data to prevent duplicate naming.

---

*Optimized for Windows, compatible with Linux and macOS.*
