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
**Author:** Music Analyzer Team
