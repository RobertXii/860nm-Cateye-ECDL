import nidaqmx
import time
import wlmData
import wlmConst
import sys
import numpy as np
import matplotlib.pyplot as plt
import time

# --- Configuration ---
DEVICE = "Dev1"
AO_CHANNEL = "ao0"
AI_CHANNEL = "ai0"
mA_per_V = 50
start_current_mA = -30
end_current_mA = 20
steps = 1000
pause = 0.01  # seconds between steps

DLL_PATH = "wlmData.dll"

# Load DLL from DLL_PATH
try:
    wlmData.LoadDLL(DLL_PATH)
except:
    sys.exit("Error: Couldn't find DLL on path %s. Please check the DLL_PATH variable!" % DLL_PATH)

# Not necessary but useful to verify connection. Can comment out.
if wlmData.dll.GetWLMCount(0) == 0:
    print("There is no running wlmServer instance(s).")
else:
    n = wlmData.dll.GetWLMCount(0)
    print(f"SUCCSESSFUL CONNECTION TO {n} SYSTEM(S)")

def GetFreq(channel=4):
    freq = wlmData.dll.GetFrequencyNum(channel, 0)
    if freq <= 0:
        print("Invalid frequency reading.")
        return None
    return freq / 1e12  # Convert Hz to THz


# --- Prepare voltage steps ---
voltages = np.linspace(start_current_mA / mA_per_V, end_current_mA / mA_per_V, steps)

# --- Storage for all data ---
all_currents = []
all_frequencies = []

# --- Sweep loop ---
with nidaqmx.Task() as ao_task, nidaqmx.Task() as ai_task:
    ao_task.ao_channels.add_ao_voltage_chan(f"{DEVICE}/{AO_CHANNEL}", min_val=-10.0, max_val=10.0)
    ai_task.ai_channels.add_ai_voltage_chan(f"{DEVICE}/{AI_CHANNEL}", min_val=0.0, max_val=10.0)

    for v in voltages:
        ao_task.write(v)
        time.sleep(pause)

        v_meas = ai_task.read()
        current_mA = v_meas * mA_per_V

        freq_thz = GetFreq()
        if freq_thz is not None:
            all_currents.append(current_mA)
            all_frequencies.append(freq_thz)


plt.figure()
plt.scatter(all_currents, np.array(all_frequencies)*1e15 - 3.48697e5, s=5, c='k', marker='o')
plt.xlabel("Laser Current (mA)")
plt.ylabel("Frequency (GHz)")
plt.title("Laser Frequency vs Current")
plt.grid(False)
plt.show()