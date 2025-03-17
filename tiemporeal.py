import sqlite3
import threading
import time
import random
import tkinter as tk
from tkinter import ttk, messagebox

MAX_ALTITUDE = 80  # Altura maxima permitida en metros
semaphore = threading.Semaphore(1)  # Semaforo para sincronizacion
def init_db():
    conn = sqlite3.connect("drone_signals.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drone_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            altitude REAL,
            speed REAL,
            processed INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS control_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            control_value REAL,
            correction REAL DEFAULT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            error_message TEXT
        )
    """)
    conn.commit()
    conn.close()

def capture_drone_signal():
    altitude = random.uniform(10, 100)
    speed = random.uniform(0, 50)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    semaphore.acquire()
    try:
        conn = sqlite3.connect("drone_signals.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO drone_signals (timestamp, altitude, speed) VALUES (?, ?, ?)", (timestamp, altitude, speed))
        conn.commit()
        conn.close()
    finally:
        semaphore.release()
    
    check_altitude_alert(altitude, timestamp)
    threading.Timer(1, capture_drone_signal).start()  # Llamada recursiva

def process_drone_signal():
    semaphore.acquire()
    try:
        conn = sqlite3.connect("drone_signals.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, altitude, speed FROM drone_signals WHERE processed = 0")
        signals = cursor.fetchall()
        for signal in signals:
            signal_id, altitude, speed = signal
            try:
                adjusted_altitude = altitude * 1.05 
                adjusted_speed = speed * 1.02
                cursor.execute("UPDATE drone_signals SET processed = 1 WHERE id = ?", (signal_id,))
                conn.commit()
            except Exception as e:
                log_error(str(e))
        conn.close()
    finally:
        semaphore.release()
    
    threading.Timer(1, process_drone_signal).start()  # Llamada recursiva

def log_error(message):
    semaphore.acquire()
    try:
        conn = sqlite3.connect("drone_signals.db")
        cursor = conn.cursor()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO errors (timestamp, error_message) VALUES (?, ?)", (timestamp, message))
        conn.commit()
        conn.close()
    finally:
        semaphore.release()

def check_altitude_alert(altitude, timestamp):
    if altitude > MAX_ALTITUDE:
        messagebox.showwarning("Alerta de Altitud", f"El dron ha superado la altura máxima permitida ({MAX_ALTITUDE} m) en {timestamp}.")
        log_error(f"Altitud excedida: {altitude} m en {timestamp}")

def fetch_latest_signals():
    semaphore.acquire()
    try:
        conn = sqlite3.connect("drone_signals.db")
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, altitude, speed FROM drone_signals ORDER BY id DESC LIMIT 10")
        signals = cursor.fetchall()
        conn.close()
        return signals
    finally:
        semaphore.release()

def update_ui():
    for row in tree.get_children():
        tree.delete(row)
    for signal in fetch_latest_signals():
        tree.insert("", "end", values=signal)
    root.after(2000, update_ui)

def main():
    init_db()
    capture_drone_signal()
    process_drone_signal()
    global root, tree
    root = tk.Tk()
    root.title("Drone Signal Monitor")
    
    columns = ("timestamp", "altitude", "speed")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    tree.heading("timestamp", text="Timestamp")
    tree.heading("altitude", text="Altitude (m)")
    tree.heading("speed", text="Speed (m/s)")
    tree.pack(expand=True, fill="both")
    
    update_ui()
    root.mainloop()

if __name__ == "__main__":
    main()