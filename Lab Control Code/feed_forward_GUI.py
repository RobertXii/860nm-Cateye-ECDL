import tkinter as tk
from tkinter import ttk
import threading
import time
import nidaqmx

# Conversion factors
mA_per_V = 50  # Laser current conversion factor
V_per_V = 15   # DAQ input to piezo voltage
k_feedforward = -7 # V/mA 15.3V/4mA = 3.825V/mA
# DAQ Channels
DEVICE_NAME = "Dev1"
AO0_CHANNEL = f"{DEVICE_NAME}/ao0"  # Laser current control
AO1_CHANNEL = f"{DEVICE_NAME}/ao1"  # Piezo voltage control
AI_CHANNEL = f"{DEVICE_NAME}/ai0"   # Current monitor

def set_laser_current(current_mA):
    voltage = current_mA / mA_per_V
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(AO0_CHANNEL, min_val=-10.0, max_val=10.0)
        task.write(voltage)

def set_piezo_voltage(voltage_V):
    voltage_daq = voltage_V / V_per_V
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(AO1_CHANNEL, min_val=0.0, max_val=10.0)
        task.write(voltage_daq)

def read_laser_current():
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(AI_CHANNEL, min_val=0.0, max_val=10.0)
        voltage = task.read()
        current_mA = voltage * mA_per_V
        return current_mA

# GUI setup
class FeedforwardGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Piezo Feedforward Control")

        self.slider = ttk.Scale(root, from_=0, to=140, orient="horizontal", length=400, command=self.on_slider_change)
        self.slider.set(0)
        self.slider.pack(pady=10)

        self.label_piezo = ttk.Label(root, text="Piezo Voltage: 0.00 V")
        self.label_piezo.pack()

        self.label_feedforward = ttk.Label(root, text="Feedforward Current: 0.00 mA")
        self.label_feedforward.pack()

        self.label_measured = ttk.Label(root, text="Measured Laser Current: 0.00 mA")
        self.label_measured.pack()

        self.running = True
        self.update_thread = threading.Thread(target=self.update_measured_current)
        self.update_thread.daemon = True
        self.update_thread.start()

    def on_slider_change(self, value):
        piezo_voltage = float(value)
        self.label_piezo.config(text=f"Piezo Voltage: {piezo_voltage:.2f} V")

        # Feedforward logic
        feedforward_current = piezo_voltage / k_feedforward
        self.label_feedforward.config(text=f"Feedforward Current: {feedforward_current:.2f} mA")

        set_piezo_voltage(piezo_voltage)
        set_laser_current(feedforward_current)

    def update_measured_current(self):
        while self.running:
            current = read_laser_current()
            self.label_measured.config(text=f"Measured Laser Current: {current:.2f} mA")
            time.sleep(0.2)  # Update every 200 ms

    def on_close(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FeedforwardGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
