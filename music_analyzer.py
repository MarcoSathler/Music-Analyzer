#!/usr/bin/env python3
"""
Script to analyze BPM and Key of multiple music files in a folder.
FEATURE: Automatically renames files with pattern: [Key] - [BPM] - [Original Name]

Requirements:
    pip install librosa numpy mutagen
"""

import csv
import json
import logging
import math
import os
import re
import shutil
import tempfile
import librosa
import mutagen
import numpy as np

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from tkinter import (
    Tk, filedialog, messagebox, simpledialog,
    Toplevel, Label, Entry, Button, Checkbutton,
    Radiobutton, StringVar, BooleanVar, Frame
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('music_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Supported audio formats
SUPPORTED_FORMATS = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}

# Camelot Mapping
CAMELOT_MAP = {
    'B': '1B', 'Bm': '1A',
    'F#': '2B', 'Gb': '2B', 'F#m': '2A', 'Gbm': '2A',
    'C#': '3B', 'Db': '3B', 'C#m': '3A', 'Dbm': '3A',
    'G#': '4B', 'Ab': '4B', 'G#m': '4A', 'Abm': '4A',
    'D#': '5B', 'Eb': '5B', 'D#m': '5A', 'Ebm': '5A',
    'A#': '6B', 'Bb': '6B', 'A#m': '6A', 'Bbm': '6A',
    'F': '7B', 'Fm': '7A',
    'C': '8B', 'Cm': '8A',
    'G': '9B', 'Gm': '9A',
    'D': '10B', 'Dm': '10A',
    'A': '11B', 'Am': '11A',
    'E': '12B', 'Em': '12A'
}


class MusicAnalyzer:
    def __init__(self, rename_files: bool = True, remove_strings: List[str] = None,
                 replace_dict: Dict[str, str] = None, key_notation: str = 'classic'):
        self.rename_files = rename_files
        self.remove_strings = remove_strings if remove_strings else []
        self.replace_dict = replace_dict if replace_dict else {}
        self.key_notation = key_notation  # 'classic' or 'camelot'
        self.renamed_count = 0
        self.rename_errors = 0

        # Krumhansl-Schmuckler Profiles (Major and Minor)
        # Source: Krumhansl (1990)
        self.major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        self.minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

        # Normalize profiles
        self.major_profile = self.major_profile / np.linalg.norm(self.major_profile)
        self.minor_profile = self.minor_profile / np.linalg.norm(self.minor_profile)

        self.keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    def detect_bpm(self, audio_path: Union[str, Path]) -> Optional[int]:
        """
        Detects BPM using librosa.
        
        Strategy:
        1. Load audio
        2. Extract onset envelope
        3. Detect beat with beat_track()
        4. Apply correction for octave error (BPM might be double/half)
        5. Custom rounding: decimal > 0.10 rounds up
        
        Returns:
            int: Calculated BPM or None if failed
        """
        try:
            logger.info(f"Analyzing BPM: {Path(audio_path).name}")

            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None)

            if len(y) == 0:
                logger.warning(f"Empty file: {audio_path}")
                return None

            # Extract onset envelope for better detection
            onset_env = librosa.onset.onset_strength(
                y=y, sr=sr, hop_length=512, aggregate=np.median
            )

            # Detect tempo and beats
            tempo, beats = librosa.beat.beat_track(
                onset_envelope=onset_env,
                sr=sr,
                hop_length=512,
                start_bpm=120,
                tightness=100
            )

            # Convert to float if necessary
            tempo = int(float(tempo))

            # Correct octave error
            if tempo < 70:
                tempo = tempo * 2
                logger.debug(f"  → BPM too low, doubling: {tempo}")
            elif tempo > 200:
                tempo = tempo / 2
                logger.debug(f"  → BPM too high, halving: {tempo}")

            logger.info(f"  ✓ BPM detected: {tempo:.2f} ")

            return tempo

        except Exception as e:
            logger.error(f"Error detecting BPM in {audio_path}: {str(e)}")
            return None

    def detect_key(self, audio_path: Union[str, Path]) -> Tuple[Optional[str], Optional[float]]:
        """
        Detects key using native Krumhansl-Schmuckler algorithm with librosa.
        
        Returns:
            tuple: (key, confidence) or (None, None)
        """
        try:
            logger.info(f"Detecting key: {Path(audio_path).name}")

            # Load only 60 seconds from the center to speed up
            duration = librosa.get_duration(path=audio_path)
            start_time = max(0, (duration / 2) - 30)

            y, sr = librosa.load(str(audio_path), sr=None, offset=start_time, duration=60)

            if len(y) == 0:
                return None, None

            # Extract Chroma (Harmonic Pitch Class Profile)
            # Use CQT for better frequency resolution
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

            # Calculate mean chroma vector
            chroma_mean = np.mean(chroma, axis=1)
            chroma_mean = chroma_mean / np.linalg.norm(chroma_mean)  # Normalize

            # Calculate correlation with all profiles
            max_corr = -1
            best_key = None

            # Loop to generate 12 rotations
            for i in range(12):
                # Major (X)
                profile_major = np.roll(self.major_profile, i)
                corr_major = np.dot(chroma_mean, profile_major)

                if corr_major > max_corr:
                    max_corr = corr_major
                    best_key = f"{self.keys[i]}"

                # Minor (Xm)
                profile_minor = np.roll(self.minor_profile, i)
                corr_minor = np.dot(chroma_mean, profile_minor)

                if corr_minor > max_corr:
                    max_corr = corr_minor
                    best_key = f"{self.keys[i]}m"  # Note + m (e.g. Cm)

            # Confidence based on correlation
            confidence = "High" if max_corr > 0.8 else "Medium" if max_corr > 0.5 else "Low"

            logger.info(f"  ✓ Key: {best_key} (corr: {max_corr:.2f})")
            return best_key, max_corr

        except Exception as e:
            logger.error(f"Error detecting key in {audio_path}: {str(e)}")
            return None, None

    def _sanitize_filename(self, filename: str) -> str:
        """Removes invalid characters for filenames."""
        invalid_chars = '<>:"/\\|?*'

        for char in invalid_chars:
            filename = filename.replace(char, '-')

        # Remove extra spaces
        filename = ' '.join(filename.split())

        return filename.strip()

    def _update_metadata(self, file_path: Path, new_title: str) -> bool:
        """Updates the 'Title' metadata tag of the audio file."""
        try:
            # mutagen.File with easy=True attempts to map common tags
            audio = mutagen.File(file_path, easy=True)

            if audio is None:
                audio = mutagen.File(file_path)

            if audio is None:
                logger.warning(f"  ⚠ Format not supported for metadata: {file_path.name}")
                return False

            # Update title
            audio['title'] = [new_title]
            audio.save()
            logger.info(f"  ✓ Metadata Title updated: '{new_title}'")
            return True

        except Exception as e:
            logger.error(f"Error updating metadata for {file_path}: {str(e)}")
            return False

    def _get_display_key(self, raw_key: str) -> str:
        """Converts key to the desired notation."""
        if self.key_notation == 'camelot':
            return CAMELOT_MAP.get(raw_key, raw_key)
        return raw_key  # Classic

    def _rename_file(self, file_path: Union[str, Path], key: str, bpm: int) -> Tuple[bool, str]:
        """
        Renames file with pattern: [Key] - [BPM] bpm - [Original Name]
        Also updates Title tag.
        Handles: Smart replacement of old notation.
        
        Returns:
            tuple: (success: bool, new_path: str)
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                logger.error(f"File not found to rename: {file_path}")
                return False, str(file_path)

            original_name = file_path.stem
            extension = file_path.suffix

            # --- NAME CLEANING ---
            # 1. Remove specific strings
            for rem_str in self.remove_strings:
                if rem_str:
                    original_name = original_name.replace(rem_str, "")

            # 2. Replace characters
            for old_char, new_char in self.replace_dict.items():
                original_name = original_name.replace(old_char, new_char)

            # -----------------------

            # Define final key (Alphanumeric or Classic)
            display_key = self._get_display_key(key)

            # --- NOTATION CONFLICT DETECTION ---
            # Check if OTHER format exists in name to remove
            
            camelot_key = CAMELOT_MAP.get(key)
            classic_key = key

            # Regex patterns
            pattern_camelot = rf"\b{re.escape(camelot_key)}\b" if camelot_key else None
            pattern_classic = rf"\b{re.escape(classic_key)}\b"

            # If we want Camelot, remove Classic if exists
            if self.key_notation == 'camelot':
                if re.search(pattern_classic, original_name, re.IGNORECASE):
                    original_name = re.sub(pattern_classic, '', original_name, flags=re.IGNORECASE)

            # If we want Classic, remove Camelot if exists
            elif self.key_notation == 'classic':
                if pattern_camelot and re.search(pattern_camelot, original_name, re.IGNORECASE):
                    original_name = re.sub(pattern_camelot, '', original_name, flags=re.IGNORECASE)

            # Remove old BPM if exists to avoid duplication
            pattern_bpm = r'\b\d+\s*bpm\b'
            original_name = re.sub(pattern_bpm, '', original_name, flags=re.IGNORECASE)

            # Clean leading spaces/hyphens
            original_name = original_name.strip()
            original_name = re.sub(r'^[\s-]*', '', original_name)

            # Clean general double spaces
            original_name = ' '.join(original_name.split())

            # -----------------------

            # Check if ALREADY has correct Key and BPM
            pattern_display = rf"\b{re.escape(display_key)}\b"
            has_correct_key = bool(re.search(pattern_display, file_path.stem, re.IGNORECASE))
            has_bpm = str(bpm) in file_path.stem

            if has_bpm and has_correct_key:
                logger.info(f"  → File already correct ({display_key}, {bpm}): {file_path.name}")
                self._update_metadata(file_path, file_path.stem)
                return True, str(file_path)

            # Construct new name: [Key] - [BPM] bpm - [Original Name]
            new_name = f"{display_key} - {bpm} BPM - {original_name}"

            # Sanitize name
            new_name = self._sanitize_filename(new_name)

            # New path
            new_file_path = file_path.parent / f"{new_name}{extension}"

            # Avoid name conflicts
            counter = 1
            while new_file_path.exists() and new_file_path != file_path:
                name_without_ext = f"{new_name}_{counter}"
                new_file_path = file_path.parent / f"{name_without_ext}{extension}"
                counter += 1

            # If new path matches old path, just update metadata
            if new_file_path == file_path:
                logger.info(f"  → Filename already correct: {file_path.name}")
                self._update_metadata(file_path, new_name)
                return True, str(file_path)

            # Rename
            shutil.move(str(file_path), str(new_file_path))
            logger.info(f"  ✓ Renamed: {file_path.name}")
            logger.info(f"     → {new_file_path.name}")

            # Update Metadata (Title)
            self._update_metadata(new_file_path, new_name)

            return True, str(new_file_path)

        except Exception as e:
            logger.error(f"Error renaming file: {str(e)}")
            return False, str(file_path)

    def analyze_file(self, audio_path: str) -> Optional[dict]:
        """Analyzes a single audio file."""
        try:
            file_path = Path(audio_path)

            # File info
            file_stats = file_path.stat()
            duration = librosa.get_duration(path=audio_path)

            # Analysis
            bpm = self.detect_bpm(audio_path)
            key, confidence = self.detect_key(audio_path)

            # Rename (if enabled and successful analysis)
            new_path = str(file_path)
            renamed = False

            if self.rename_files and bpm is not None and key is not None:
                success, new_path_str = self._rename_file(audio_path, key, bpm)
                if success:
                    renamed = True
                    self.renamed_count += 1
                    file_path = Path(new_path_str)
                else:
                    self.rename_errors += 1

            result = {
                'original_filename': Path(audio_path).name,
                'filename': file_path.name,
                'path': str(file_path),
                'bpm': bpm,
                'key': key,
                'confidence': confidence,
                'duration_seconds': round(duration, 2),
                'size_mb': round(file_stats.st_size / (1024 * 1024), 2),
                'timestamp': datetime.now().isoformat(),
                'renamed': renamed
            }

            return result

        except Exception as e:
            logger.error(f"Error analyzing {audio_path}: {str(e)}")
            return None

    def analyze_folder(self, folder_path: str, output_format: str = 'csv') -> List[dict]:
        """Analyzes all audio files in a folder."""
        folder = Path(folder_path)

        if not folder.exists():
            logger.error(f"Folder not found: {folder}")
            return []

        # Find audio files
        audio_files = []
        for ext in SUPPORTED_FORMATS:
            audio_files.extend(folder.glob(f'*{ext}'))
            audio_files.extend(folder.glob(f'*{ext.upper()}'))

        audio_files = list(set(audio_files))  # Remove duplicates

        if not audio_files:
            logger.warning(f"No audio files found in: {folder}")
            return []

        logger.info(f"Found {len(audio_files)} files to analyze")

        results = []
        for i, audio_file in enumerate(sorted(audio_files), 1):
            logger.info(f"[{i}/{len(audio_files)}] Processing: {audio_file.name}")

            result = self.analyze_file(str(audio_file))
            if result:
                results.append(result)

            logger.info("-" * 80)

        # Save results
        if results:
            self._save_results(results, folder, output_format)

        return results

    def _save_results(self, results: List[dict], folder: Path, output_format: str = 'csv'):
        """Saves results to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if output_format == 'csv':
            output_file = folder / f'music_analysis_{timestamp}.csv'

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        'original_filename', 'filename', 'path', 'bpm', 'key', 'confidence',
                        'duration_seconds', 'size_mb', 'renamed', 'timestamp'
                    ]
                )
                writer.writeheader()
                writer.writerows(results)

            logger.info(f"Results saved to: {output_file}")

        elif output_format == 'json':
            output_file = folder / f'music_analysis_{timestamp}.json'

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info(f"Results saved to: {output_file}")

    def print_summary(self, results: List[dict]):
        """Prints analysis summary."""
        if not results:
            print("\n⚠️  No results to display")
            return

        print("\n" + "=" * 100)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 100)

        # Stats
        bpms = [r['bpm'] for r in results if r['bpm']]
        keys = [r['key'] for r in results if r['key']]

        if bpms:
            print(f"\n🎵 BPM")
            print(f"  Average: {np.mean(bpms):.2f}")
            print(f"  Min: {min(bpms)}")
            print(f"  Max: {max(bpms)}")
            print(f"  Std Dev: {np.std(bpms):.2f}")

        if keys:
            print(f"\n🔑 Keys Found:")
            key_count = defaultdict(int)
            for key in keys:
                key_count[key] += 1

            for key, count in sorted(key_count.items(), key=lambda x: x[1], reverse=True):
                print(f"  {key}: {count}x")

        # Rename stats
        print(f"\n📁 Rename Summary:")
        print(f"  Total files: {len(results)}")
        print(f"  Renamed: {self.renamed_count}")
        print(f"  Errors: {self.rename_errors}")

        print("=" * 100 + "\n")

        # Detailed table
        print("📋 DETAILS:")
        print("-" * 120)
        print(f"{'Original File':<30} {'New File':<40} {'BPM':<7} {'Key':<12}")
        print("-" * 120)

        for r in results:
            orig = r['original_filename']
            if len(orig) > 30:
                orig = orig[:27] + "..."
            
            new_f = r['filename']
            if len(new_f) > 40:
                new_f = new_f[:37] + "..."

            bpm_str = f"{r['bpm']}" if r['bpm'] else "N/A"
            key_str = r['key'] if r['key'] else "N/A"

            print(f"{orig:<30} {new_f:<40} {bpm_str:<7} {key_str:<12}")

        print("-" * 120 + "\n")


class ConfigDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None):
        self.result_data = None
        super().__init__(parent, title)

    def body(self, master):
        # Rename Frame
        self.var_rename = BooleanVar(value=True)
        cb_rename = Checkbutton(master, text="Rename Files", variable=self.var_rename)
        cb_rename.grid(row=0, column=0, sticky="w", padx=5, pady=5, columnspan=2)

        # Notation Frame
        Label(master, text="Key Notation:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.var_notation = StringVar(value="classic")
        rb_classic = Radiobutton(master, text="Classic (Cm)", variable=self.var_notation, value="classic")
        rb_camelot = Radiobutton(master, text="Camelot (8A)", variable=self.var_notation, value="camelot")
        rb_classic.grid(row=2, column=0, sticky="w", padx=20)
        rb_camelot.grid(row=3, column=0, sticky="w", padx=20)

        # Remove Strings
        Label(master, text="Remove Text (comma sep.):").grid(row=4, column=0, sticky="w", padx=5, pady=(10, 0))
        self.entry_remove = Entry(master, width=40)
        self.entry_remove.grid(row=5, column=0, padx=5, pady=2)
        Label(master, text="Ex: Official Video, [HD]", fg="gray", font=("Arial", 8)).grid(row=6, column=0, sticky="w",
                                                                                         padx=5)

        # Replace Characters
        Label(master, text="Replace Chars (old:new):").grid(row=7, column=0, sticky="w", padx=5, pady=(10, 0))
        self.entry_replace = Entry(master, width=40)
        self.entry_replace.grid(row=8, column=0, padx=5, pady=2)
        Label(master, text="Ex: _: , -:|", fg="gray", font=("Arial", 8)).grid(row=9, column=0, sticky="w", padx=5)

        return cb_rename  # Initial focus

    def apply(self):
        rename = self.var_rename.get()
        notation = self.var_notation.get()

        # Parse Remove
        rem_text = self.entry_remove.get()
        remove_strings = [s.strip() for s in rem_text.split(',') if s.strip()]

        # Parse Replace
        rep_text = self.entry_replace.get()
        replace_dict = {}
        try:
            pairs = [p.strip() for p in rep_text.split(',') if p.strip()]
            for p in pairs:
                if ':' in p:
                    k, v = p.split(':', 1)
                    if k:
                        replace_dict[k] = v
        except Exception:
            pass

        self.result_data = {
            'rename': rename,
            'notation': notation,
            'remove_strings': remove_strings,
            'replace_dict': replace_dict
        }


def main():
    """Main function with GUI."""
    
    # Create hidden root window
    root = Tk()
    root.withdraw()

    folder = filedialog.askdirectory(
        title="Select Music Folder",
        initialdir=os.path.expanduser("~/Music")
    )

    if not folder:
        messagebox.showinfo("Cancelled", "Operation cancelled by user")
        return

    # Open unified config dialog
    dialog = ConfigDialog(root, title="Analysis Configuration")

    if not dialog.result_data:
        print("Operation cancelled in configuration.")
        return

    config = dialog.result_data
    rename_choice = config['rename']
    key_notation = config['notation']
    remove_strings = config['remove_strings']
    replace_dict = config['replace_dict']

    print("\n" + "=" * 100)
    print("🎼 MUSIC ANALYZER - BPM, KEY & RENAMER")
    print("=" * 100)
    print(f"📁 Folder: {folder}")
    print(f"🔄 Rename: {'YES' if rename_choice else 'NO'}")
    print(f"🎵 Notation: {key_notation.title()}")
    if remove_strings:
        print(f"✂️ Remove: {remove_strings}")
    if replace_dict:
        print(f"🔁 Replace: {replace_dict}")
    print()

    # Initialize analyzer
    analyzer = MusicAnalyzer(
        rename_files=rename_choice,
        remove_strings=remove_strings,
        replace_dict=replace_dict,
        key_notation=key_notation
    )

    print("📦 Resources available:")
    print(f"  ✓ librosa (BPM & Key)")
    print(f"  ✓ Notation: {'Camelot/Alphanumeric' if key_notation == 'camelot' else 'Classic'}")

    # Run analysis
    try:
        results = analyzer.analyze_folder(folder, output_format='csv')
        analyzer.print_summary(results)

        if results:
            if rename_choice:
                messagebox.showinfo(
                    "Success",
                    f"✓ Analysis and Renaming complete!\n\n"
                    f"Files processed: {len(results)}\n"
                    f"Renamed: {analyzer.renamed_count}\n"
                    f"Errors: {analyzer.rename_errors}\n\n"
                    f"Results saved in: {folder}"
                )
            else:
                messagebox.showinfo(
                    "Success",
                    f"✓ Analysis complete!\n\n"
                    f"Files processed: {len(results)}\n"
                    f"Results saved in: {folder}"
                )

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        messagebox.showerror("Error", f"Error during analysis:\n{str(e)}")


if __name__ == "__main__":
    main()
