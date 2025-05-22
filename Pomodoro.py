import kivy
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
import sqlite3
import time

kivy.require("2.1.0")

# Inisialisasi Database
conn = sqlite3.connect("pomodoro_history.db")
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY,
        timestamp TEXT,
        duration TEXT
    )
""")
conn.commit()

class PomodoroScreen(Screen):
    current_time = NumericProperty(25 * 60)  # 25 menit (dalam detik)
    timer_text = StringProperty("25:00")
    running = False
    popup = None  # Menyimpan referensi popup

    def start_pause(self):
        self.running = not self.running
        if self.running:
            Clock.schedule_interval(self.countdown, 1)
        else:
            Clock.unschedule(self.countdown)

    def countdown(self, dt):
        if self.current_time > 0:
            self.current_time -= 1
            mins, secs = divmod(self.current_time, 60)
            self.timer_text = f"{mins:02d}:{secs:02d}"
        else:
            self.show_alert()
            self.save_session()

    def reset(self):
        self.running = False
        Clock.unschedule(self.countdown)
        self.current_time = int(self.ids.work_duration.text) * 60
        self.timer_text = f"{int(self.current_time/60):02d}:00"

    def show_alert(self):
        # Hapus sound jika ada yang masih berjalan
        if hasattr(self, 'alert_sound') and self.alert_sound:
            self.alert_sound.stop()
            del self.alert_sound
        
        # Muat ulang suara
        self.alert_sound = SoundLoader.load("NEGEV_ATTACK_JP.mp3")
        if self.alert_sound:
            self.alert_sound.loop = True  # Aktifkan looping
            self.alert_sound.play()
            
            # Hentikan suara setelah 10 detik
            Clock.schedule_once(lambda dt: self.stop_alert(), 10)
        
        # Tambahkan tombol "OK" untuk menghentikan suara dan menutup popup
        content = BoxLayout(orientation='vertical')
        label = Label(text='Waktu kerja selesai!')
        button = Button(text='OK', size_hint=(1, 0.3))
        button.bind(on_release=lambda instance: self.stop_alert(self.popup))  # Perubahan di sini
        
        content.add_widget(label)
        content.add_widget(button)
        
        self.popup = Popup(  # Simpan referensi popup
            title="Selesai",
            content=content,
            size_hint=(None, None),
            size=(400, 200)
        )
        self.popup.open()

    def stop_alert(self, popup=None):
        if hasattr(self, 'alert_sound') and self.alert_sound:
            self.alert_sound.stop()
            del self.alert_sound
        
        if popup:
            popup.dismiss()  # Tutup popup jika ada

    def save_session(self):
        duration = f"{int(self.current_time/60)} menit"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO sessions (timestamp, duration) VALUES (?, ?)",
                 (timestamp, duration))
        conn.commit()

class HistoryScreen(Screen):
    history_text = StringProperty("")

    def on_pre_enter(self):
        self.update_history()

    def update_history(self):
        c.execute("SELECT * FROM sessions ORDER BY timestamp DESC")
        rows = c.fetchall()
        history = "\n".join([f"{row[1]} - {row[2]}" for row in rows])
        self.history_text = history if history else "Belum ada riwayat."

class PomodoroApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PomodoroScreen(name="main"))
        sm.add_widget(HistoryScreen(name="history"))
        return sm

    def on_stop(self):
        conn.close()

if __name__ == "__main__":
    PomodoroApp().run()