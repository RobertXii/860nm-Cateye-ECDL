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
end_voltage = 140      # Max piezo voltage
steps = 2000
pause = 0.01           # seconds between steps
k_feedforward = -23.9  # best -23.9 V per A (or something similar depending on context)

# Load WLM DLL
try:
    wlmData.LoadDLL("wlmData.dll")
except:
    sys.exit("Error: Couldn't load DLL — check DLL path and name.")

# Check WLM connection
if wlmData.dll.GetWLMCount(0) == 0:
    sys.exit("No WLM instance found.")
else:
    print(f"Connected to {wlmData.dll.GetWLMCount(0)} WLM system(s)")

def GetFreq(channel=4):
    freq = wlmData.dll.GetFrequencyNum(channel, 0)
    if freq <= 0:
        print("Invalid frequency reading.")
        return None
    return freq*1e3  # THz

freqs = []

for i in range(100):
    print(i)
    # Get frequency from wavemeter (in THz)
    freqs.append(GetFreq())
    time.sleep(0.1)
print(np.mean(freqs))
print(np.std(freqs))    