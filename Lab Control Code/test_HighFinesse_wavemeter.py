import time
import numpy as np
import wlmData
import wlmConst
import sys

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


def GetFreq():
    ### Function that gets frequency and wavelength of latest measurement
    try:
        frequency = wlmData.dll.GetFrequencyNum(4, 0)
    # All listed errors in the manual:
    except wlmConst.ErrNoValue:
        print("dll is instantiated with return mode = 1")
    except wlmConst.ErrNoSignal:
        print("The Wavelength Meter has not detected any signal.")
    except wlmConst.ErrBadSignal:
        print("The Wavelength Meter has not detected a calculable signal. ")
    except wlmConst.ErrLowSignal: 
        print("The signal is too small to be calculated properly. ")
    except wlmConst.ErrBigSignal: 
        print("The signal is too large to be calculated properly, this can happen if the amplitude of the signal is electronically cut caused by stack overflow. ")
    except wlmConst.ErrNoPulse:
        print("The detected signal could not be divided into separated pulses. ")
    except wlmConst.ErrWlmMissing: 
        print("The Wavelength Meter is not active. ")
    except wlmConst.ErrNotAvailable:
        print("This called function is not available for this version of Wavelength Meter.") 
    return frequency

freq = GetFreq()
print(f"Frequency: {freq:.8f} THz")


