import time
from tts import speak

class TimeBuffer:
    def __init__(self, timeout=3):
        self.timeout = timeout

        self.current_word = []          # simpan huruf sebagai list
        self.last_gesture = None        # huruf terakhir
        self.gesture_start_time = None  # waktu gesture mulai

    def update(self, gesture):
        now = time.time()

        if gesture:
            # gesture baru
            if gesture != self.last_gesture:
                # simpan gesture sebelumnya
                if self.last_gesture is not None:
                    self.current_word.append(self.last_gesture)

                self.last_gesture = gesture
                self.gesture_start_time = now

            return "".join(self.current_word) + self.last_gesture

        else:
            # tidak ada gesture → cek timeout
            if self.last_gesture and (now - self.gesture_start_time) >= self.timeout:
                # simpan huruf terakhir
                self.current_word.append(self.last_gesture)

                final_text = "".join(self.current_word)
                speak(final_text)

                # reset
                self.current_word = []
                self.last_gesture = None
                self.gesture_start_time = None

        return "".join(self.current_word)

    def get_and_clear_ready_sentence(self):
        # tidak dipakai lagi (TTS otomatis)
        return None
