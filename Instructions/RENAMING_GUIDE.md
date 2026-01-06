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
