import pygame
import time
import threading
from gtts import gTTS

# Inisialisasi mixer
pygame.mixer.init()

def test_speak(text):
    print(f"Memproses suara: {text}")
    tts = gTTS(text=text, lang="id")
    tts.save("test_output.mp3")
    
    pygame.mixer.music.load("test_output.mp3")
    pygame.mixer.music.play()
    print("Suara mulai diputar di latar belakang...")

# SIMULASI KAMERA (Looping tetap berjalan saat suara berbunyi)
print("Memulai simulasi loop kamera...")
test_speak("Halo, sistem siap digunakan")

for i in range(1, 11):
    print(f"Frame kamera ke-{i}: Tracking aktif...")
    time.sleep(0.5)  # Simulasi jeda frame

print("Test berhasil, jika mendengar suara sambil melihat tulisan 'Frame kamera'")
