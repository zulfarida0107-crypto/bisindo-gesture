"""
tts.py — Text-to-Speech engine untuk BISINDO
Queue-based agar tidak overlap dan non-blocking.
"""

import queue
import threading
import time
import os
import tempfile

# ─── Coba import TTS engine ─────────────────────────────────────
_use_pyttsx3 = False
_use_gtts = False

try:
    import pyttsx3
    _use_pyttsx3 = True
except ImportError:
    pass

if not _use_pyttsx3:
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
    Otomatis memilih engine terbaik:
      1. pyttsx3 (offline, cepat)
      2. gTTS + pygame (online, lebih natural)
    """

    def __init__(self):
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

        if _use_gtts:
            print("  TTS Engine: gTTS + pygame (online, natural Indonesian female)")
        elif _use_pyttsx3:
            print("  TTS Engine: pyttsx3 (offline)")
        else:
            print("  TTS Engine: TIDAK TERSEDIA")
            print("  Install salah satu: pip install pyttsx3  ATAU  pip install gTTS pygame")

    def speak(self, text):
        """Non-blocking: masukkan text ke queue untuk dibaca."""
        if text and text.strip():
            self._queue.put(text.strip())

    def _worker(self):
        """Background worker yang memproses queue TTS."""
        while True:
            text = self._queue.get()

            try:
                # Ambil item terbaru, skip yang lama
                while not self._queue.empty():
                    try:
                        text = self._queue.get_nowait()
                    except queue.Empty:
                        break

                # Prioritaskan gTTS (Suara wanita Indonesia)
                if _use_gtts:
                    try:
                        self._speak_gtts(text)
                    except Exception as e:
                        print(f"  [TTS] gTTS gagal ({e}), fallback ke pyttsx3")
                        if _use_pyttsx3:
                            self._speak_pyttsx3(text)
                elif _use_pyttsx3:
                    self._speak_pyttsx3(text)
                else:
                    print(f"  [TTS tidak aktif] Teks: {text}")

            except Exception as e:
                print(f"  TTS Error: {e}")

    @staticmethod
    def _speak_pyttsx3(text):
        """Baca teks menggunakan pyttsx3 (offline)."""
        engine = pyttsx3.init()
        
        # Coba cari suara bahasa Indonesia (prioritaskan wanita)
        voices = engine.getProperty('voices')
        selected_voice = None
        for voice in voices:
            name_lower = voice.name.lower()
            if 'indonesia' in name_lower or 'id-' in voice.id.lower() or 'gadis' in name_lower:
                selected_voice = voice.id
                # Jika ada nama "gadis" atau indikasi female, jadikan prioritas utama
                if 'gadis' in name_lower or 'female' in name_lower:
                    break
        
        if selected_voice:
            engine.setProperty('voice', selected_voice)

        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        engine.stop()

    @staticmethod
    def _speak_gtts(text):
        """Baca teks menggunakan gTTS + pygame (online)."""
        temp_dir = tempfile.gettempdir()
        filename = os.path.join(
            temp_dir, f"bisindo_tts_{int(time.time() * 1000)}.mp3"
        )

        try:
            tts = gTTS(text=text, lang="id")
            tts.save(filename)

            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.music.unload()
            time.sleep(0.2)

            if os.path.exists(filename):
                os.remove(filename)

        except Exception as e:
            print(f"  gTTS Error: {e}")
            try:
                pygame.mixer.music.unload()
            except Exception:
                pass


# ─── Singleton instance ─────────────────────────────────────────
_engine = None


def get_tts_engine():
    """Dapatkan singleton TTSEngine."""
    global _engine
    if _engine is None:
        _engine = TTSEngine()
    return _engine


def speak(text):
    """Shortcut untuk get_tts_engine().speak(text)."""
    get_tts_engine().speak(text)