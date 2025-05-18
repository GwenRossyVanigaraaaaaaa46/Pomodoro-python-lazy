import tkinter as tk
from tkinter import messagebox
from threading import Thread
from playsound import playsound
import time
import sqlite3



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


# Konfigurasi jendela utama
root = tk.Tk()
root.title("Pomodoro Timer")
root.geometry("400x300")  # Ukuran jendela

# Variabel global untuk kontrol timer
running = False
current_time = 25 * 60  # 25 menit (default Pomodoro)

# Fungsi untuk menghitung mundur
def countdown():
    global current_time, running
    while running and current_time >= 0:
        mins, secs = divmod(current_time, 60)
        timer_label.config(text=f"{mins:02d}:{secs:02d}")
        time.sleep(1)
        current_time -= 1
    if current_time < 0:
        playsound("NEGEV_ATTACK_JP.mp3")  # Ganti dengan path suara alarm
        messagebox.showinfo("Selesai", "Waktu kerja selesai!")

# Fungsi untuk tombol Start/Pause
def start_pause():
    global running
    if not running:
        running = True
        thread = Thread(target=countdown)
        thread.start()
    else:
        running = False

# Fungsi untuk tombol Reset
def reset():
    global current_time, running
    running = False
    current_time = 25 * 60
    timer_label.config(text="25:00")

# Membuat widget GUI
timer_label = tk.Label(root, text="25:00", font=("Arial", 48))
timer_label.pack(pady=20)

start_button = tk.Button(root, text="Start/Pause", command=start_pause)
start_button.pack()

reset_button = tk.Button(root, text="Reset", command=reset)
reset_button.pack()

work_duration = tk.IntVar(value=25)  # Menit
break_duration = tk.IntVar(value=5)  # Menit

work_entry = tk.Entry(root, textvariable=work_duration)
work_entry.pack()

break_entry = tk.Entry(root, textvariable=break_duration)
break_entry.pack()

# Ubah warna latar belakang
root.configure(bg="#2c3e50")

# Ubah warna teks timer
timer_label.config(fg="#ecf0f1", bg="#2c3e50")

# Ubah gaya tombol
start_button.config(bg="#2ecc71", fg="white", font=("Arial", 12))
reset_button.config(bg="#e74c3c", fg="white", font=("Arial", 12))




# Loop utama aplikasi
root.mainloop()

# Fungsi untuk menyimpan sesi
def save_session(duration):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO sessions (timestamp, duration) VALUES (?, ?)", (timestamp, duration))
    conn.commit()

# Fungsi untuk menampilkan riwayat
def show_history():
    history_window = tk.Toplevel(root)
    history_window.title("Riwayat Sesi")
    history_list = tk.Listbox(history_window, width=50)
    history_list.pack(pady=20)

    # Ambil data dari database
    c.execute("SELECT * FROM sessions ORDER BY timestamp DESC")
    rows = c.fetchall()
    for row in rows:
        history_list.insert(tk.END, f"{row[1]} - {row[2]}")

# Tambahkan tombol History
history_button = tk.Button(root, text="History", command=show_history)
history_button.pack()
