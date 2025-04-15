import nidaqmx
import time
import wlmData
import wlmConst
import sys
import numpy as np
import matplotlib.pyplot as plt

# --- Configuration ---
DEVICE = "Dev1"
AO1_CHANNEL = "ao1"  # Piezo voltage
AO0_CHANNEL = "ao0"  # Laser current (feedforward)
V_per_V = 15
start_voltage = 0      # Piezo voltage in V
end_voltage = 150      # Max piezo voltage
steps = 1000
pause = 0.01           # seconds between steps
k_feedforward = -27  # V per A (or something similar depending on context)

# Load WLM DLL
try:
    wlmData.LoadDLL("wlmData.dll")
except:
    sys.exit("Error: Couldn't load DLL — check DLL path and name.")

# Check WLM connection
if wlmData.dll.GetWLMCount(0) == 0:
    sys.exit("No WLM instance found.")
else:
    print(f"✅ Connected to {wlmData.dll.GetWLMCount(0)} WLM system(s)")

# Get frequency from wavemeter (in THz)
def GetFreq(channel=4):
    freq = wlmData.dll.GetFrequencyNum(channel, 0)
    if freq <= 0:
        print("⚠️ Invalid frequency reading.")
        return None
    return freq / 1e12  # THz

# --- Generate piezo control voltages ---
voltages_daq = np.linspace(start_voltage / V_per_V, end_voltage / V_per_V, steps)

# --- Data storage ---
all_piezo_voltages = []
all_frequencies = []

# --- Sweep with DAQ ---
with nidaqmx.Task() as ao1_task, nidaqmx.Task() as ao0_task:
    ao1_task.ao_channels.add_ao_voltage_chan(f"{DEVICE}/{AO1_CHANNEL}", min_val=0.0, max_val=10.0)
    ao0_task.ao_channels.add_ao_voltage_chan(f"{DEVICE}/{AO0_CHANNEL}", min_val=-10.0, max_val=10.0)

    for v_daq in voltages_daq:
        # Set voltages
        ao1_task.write(v_daq)  # Piezo
        ao0_task.write(v_daq / k_feedforward)  # Feedforward to laser diode

        time.sleep(pause)

        # Convert back to physical piezo voltage
        piezo_voltage_V = v_daq * V_per_V

        # Get frequency
        freq_thz = GetFreq()
        if freq_thz is not None:
            all_piezo_voltages.append(piezo_voltage_V)
            all_frequencies.append(freq_thz)

# --- Plot ---
plt.figure()
plt.scatter(all_piezo_voltages, np.array(all_frequencies)*1e15 - 3.48697e5, s=5, c='k', marker='o')
plt.xlabel("Piezo Voltage (V)")
plt.ylabel("Frequency Offset (GHz)")
plt.title("Laser Frequency vs Piezo Voltage (with feedforward current)")
plt.grid(True)
plt.tight_layout()
plt.show()
