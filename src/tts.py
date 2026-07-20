"""
tts.py — Text-to-Speech engine untuk BISINDO
Menggunakan Windows SAPI via PowerShell (paling reliable di Windows).

Fallback chain:
  1. Windows SAPI (PowerShell) — built-in, bekerja setiap kali
  2. gTTS + pygame             — online, suara Indonesia natural
  3. pyttsx3                   — offline fallback
"""

import queue
import subprocess
import threading
import time
import os
import sys
import tempfile
import warnings

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")
warnings.filterwarnings("ignore", category=FutureWarning)

# ─── Deteksi platform & engine ──────────────────────────────────
IS_WINDOWS = sys.platform == "win32"
_use_gtts  = False

if not IS_WINDOWS:
    try:
        from gtts import gTTS
        import pygame
        pygame.mixer.init()
        _use_gtts = True
    except ImportError:
        pass


class TTSEngine:
    """
    Thread-safe TTS engine dengan queue.

    Windows : Pakai SAPI via PowerShell — paling reliable, tidak pernah crash,
              bekerja berulang kali tanpa batasan.
    Non-Win : gTTS + pygame (online) atau pyttsx3.
    """

    def __init__(self):
        self._queue  = queue.Queue()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

        if IS_WINDOWS:
            print("  TTS Engine: Windows SAPI (built-in, reliable)")
        elif _use_gtts:
            print("  TTS Engine: gTTS + pygame (online)")
        else:
            print("  TTS Engine: pyttsx3 (offline fallback)")

    def speak(self, text):
        """Non-blocking: masukkan text ke queue untuk dibaca."""
        if not text or not text.strip():
            return

        # Buang antrian lama — hanya baca yang terbaru
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

        self._queue.put(text.strip())

    def _worker(self):
        """Background thread — memproses satu teks per waktu."""
        while True:
            text = self._queue.get()
            try:
                if IS_WINDOWS:
                    self._speak_sapi(text)
                elif _use_gtts:
                    self._speak_gtts(text)
                else:
                    self._speak_pyttsx3(text)
            except Exception as e:
                print(f"  [TTS] Error: {e}")

    # ─── SAPI via PowerShell (Windows) ──────────────────────────

    @staticmethod
    def _speak_sapi(text):
        """
        Gunakan Windows Speech API via PowerShell.
        Fresh process setiap panggilan = tidak pernah crash/silent.
        """
        # Escape single quotes untuk PowerShell string
        safe_text = text.replace("'", " ").replace('"', " ")

        ps_script = (
            "Add-Type -AssemblyName System.Speech; "
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            "$s.Rate = 1; "          # -10 (lambat) sampai 10 (cepat), 1 = sedikit lebih cepat dari default
            "$s.Volume = 100; "
            f"$s.Speak('{safe_text}')"
        )

        proc = subprocess.Popen(
            [
                "powershell",
                "-WindowStyle", "Hidden",
                "-NonInteractive",
                "-NoProfile",
                "-Command", ps_script,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,  # Tidak muncul jendela konsol
        )
        proc.wait()  # Tunggu sampai selesai berbicara

    # ─── gTTS + pygame (Non-Windows / online) ───────────────────

    @staticmethod
    def _speak_gtts(text):
        temp_dir  = tempfile.gettempdir()
        filename  = os.path.join(temp_dir, f"bisindo_tts_{int(time.time()*1000)}.mp3")
        try:
            from gtts import gTTS
            import pygame
            tts = gTTS(text=text, lang="id")
            tts.save(filename)
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.music.unload()
        except Exception as e:
            print(f"  [gTTS] Error: {e}")
        finally:
            time.sleep(0.1)
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except Exception:
                    pass

    # ─── pyttsx3 (fallback terakhir) ────────────────────────────

    @staticmethod
    def _speak_pyttsx3(text):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", 150)
            engine.setProperty("volume", 1.0)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"  [pyttsx3] Error: {e}")


# ─── Singleton ──────────────────────────────────────────────────
_engine: TTSEngine | None = None


def get_tts_engine() -> TTSEngine:
    global _engine
    if _engine is None:
        _engine = TTSEngine()
    return _engine


def speak(text: str) -> None:
    """Shortcut: langsung baca teks via TTS engine."""
    get_tts_engine().speak(text)