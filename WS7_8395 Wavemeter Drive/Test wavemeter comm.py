# Importing stuff not from example header
import time
import numpy as np

# Header provided in examples used to communicate and verify comms with the wavemeter

# wlmData.dll related imports
import wlmData
import wlmConst

# others
import sys

#########################################################
# Set the DLL_PATH variable according to your environment
#########################################################
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

def GetFreqAndWL(channel):
    ### Function that gets frequency and wavelength of latest measurement
    try:
        frequency = wlmData.dll.GetFrequencyNum(channel, 0)
        wavelength = wlmData.dll.GetWavelengthNum(channel, 0)
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
    return (frequency, wavelength)

def measurement_START():
    wlmData.dll.Operation(wlmConst.cCtrlStartMeasurement)
    # Determines the state of operations and prints representative integer. Used for testing.
    #opstate = wlmData.dll.GetOperationState(0)
    #print(opstate)

def measurement_STOP():
    wlmData.dll.Operation(wlmConst.cCtrlStopAll)
    # Determines the state of operations and prints representative integer. Used for testing.
    #opstate = wlmData.dll.GetOperationState(0)
    #print(opstate)

def measure_for_time(t):
    ## Starts a measurement that lasts t seconds
    measurement_START()
    time.sleep(t)
    measurement_STOP()


def change_ref_by_x(x):
    # Function that changes deviation reference by a number x, and then returns the deviation reference
    curr_ref = wlmData.dll.GetDeviationReference(0)
    print(curr_ref)
    wlmData.dll.SetDeviationReference(curr_ref + x)
    return wlmData.dll.GetDeviationReference(0)

#devmode = wlmData.dll.GetDeviationMode(0)
#print(devmode)

# Just running functions to test
#for j in range(5):
#    tpl = GetFreqAndWL(1)
#    time.sleep(0.01)
#    print(f"From channel {1}: {tpl}")


def ZieglerNicholsMethod():
    # First set all params to 0 and then increase K_p until a stable oscillation is detected
    # Need a function that will detect oscillation
    # Then use oscillation detection to figure out period of oscillation
    # From period T_u determine T_i and T_d using ZN method (Classic PID)
    raise NotImplementedError

def getLinewidth_STDEV(channel, n, interval):
    ### Function that returns the standard deviation in megaherz of a set of frequencies of length n
    ### sampled with an interval of "interval" seconds
    freq_lst = []
    for j in range(n):
        tpl = GetFreqAndWL(channel)
        time.sleep(interval)
        #print(tpl[0])
        freq_lst.append(tpl[0])
    array = np.array(freq_lst)
    #print(array)
    return float(np.std(array) * (10**6))

def SetPIDparams(P, I, D, port):
    # Set P param
    wlmData.dll.SetPIDSetting(wlmConst.cmiPID_P, port, 0, P)
    # Set I param
    wlmData.dll.SetPIDSetting(wlmConst.cmiPID_I, port, 0, I)
    # Set D param
    wlmData.dll.SetPIDSetting(wlmConst.cmiPID_D, port, 0, D)

LW1 = getLinewidth_STDEV(1, 1000, 0.01)
print(f"Linewidth in MHz: {LW1}")

# Log environmental stuff