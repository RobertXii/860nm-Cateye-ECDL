import nidaqmx
import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import time
print(pyvisa.__version__)

# --- Configuration ---
DEVICE = "Dev1"
AO_CHANNEL = "ao0"
AI_CHANNEL = "ai0"
mA_per_V = 50
start_current_mA = 50
end_current_mA = 250
steps = 50
pause = 0.2  # seconds between steps

# --- Initialize VISA ---
rm = pyvisa.ResourceManager()
wavemeter = rm.open_resource("GPIB0::20::INSTR")  # Replace with your address
wavemeter.timeout = 3000

# --- Prepare voltage steps ---
voltages = np.linspace(start_current_mA / mA_per_V, end_current_mA / mA_per_V, steps)

# --- Storage for all data ---
all_currents = []
all_frequencies = []

# --- Sweep loop ---
with nidaqmx.Task() as ao_task, nidaqmx.Task() as ai_task:
    ao_task.ao_channels.add_ao_voltage_chan(f"{DEVICE}/{AO_CHANNEL}")
    ai_task.ai_channels.add_ai_voltage_chan(f"{DEVICE}/{AI_CHANNEL}", min_val=0.0, max_val=10.0)

    for v in voltages:
        ao_task.write(v)
        time.sleep(pause)

        # Measure actual current
        v_meas = ai_task.read()
        current_mA = v_meas * mA_per_V

        # Get all frequencies (comma-separated)
        try:
            resp = wavemeter.query(":FETCH:ARRAY:SCALAR:FREQ?")
            freq_list = [float(f.strip()) for f in resp.split(",") if f]
            freq_THz = [f / 1e12 for f in freq_list]
        except Exception as e:
            print(f"Error reading frequencies: {e}")
            freq_THz = []

        # Store current for each detected frequency
        all_currents.extend([current_mA] * len(freq_THz))
        all_frequencies.extend(freq_THz)

        print(f"{current_mA:.1f} mA → {len(freq_THz)} lines: {freq_THz}")

# --- Plot ---
plt.figure()
plt.scatter(all_currents, all_frequencies, marker='o')
plt.xlabel("Laser Current (mA)")
plt.ylabel("Frequency (THz)")
plt.title("Multi-Line Laser Spectrum vs Current")
plt.grid(True)
plt.show()