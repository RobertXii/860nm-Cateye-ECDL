# Laser Current and Frequency Control System

This project sets up a complete experimental control system for a tunable laser using:

- Thorlabs **LDC205C** (laser current controller)
- Thorlabs **MDT694** (piezo voltage controller)
- National Instruments **USB-6002 DAQ** (for analog control and monitoring)
- Keysight **86120B Wavemeter** (for measuring laser frequency)
- Python with `nidaqmx` and `pyvisa` libraries

It enables you to:
- Set and ramp the laser current programmatically
- Monitor the actual current via analog feedback
- Read frequency/wavelength measurements from the wavemeter
- Plot real-time current vs. frequency behavior


## Required Hardware

| Device              | Function                          |
|---------------------|-----------------------------------|
| LDC205C             | Laser diode current control       |
| MDT694              | piezo voltage control       |
| NI USB-6002         | Analog output/input interface     |
| Keysight 86120B     | Optical frequency/wavelength meter|
| GPIB-USB-HS Adapter | Connect wavemeter to PC via GPIB  |
| BNC cables          | Analog voltage wiring             |


## 1. Hardware Wiring Guide

### A. Laser Current Control (LDC205C)

The LDC205C receives a voltage on the **MOD IN** port to set the laser current, and outputs a voltage on **CTL OUT** to report actual current.

| NI USB-6002 Pin | Connects To                | Function                 |
|-----------------|-----------------------------|--------------------------|
| AO0             | LDC205C MOD IN (R2 center) | Set laser current        |
| AO GND          | MOD IN shield              | Ground                   |
| AI0             | CTL OUT (R3 center)        | Read actual current      |
| AI GND          | CTL OUT shield             | Ground                   |

> **Conversion**: 1 V = 50 mA (Current limit = 500 mA on LDC205C)

### B. Piezo Voltage Control (MDT694)

The MDT694 receives a voltage on the **MOD IN** port to set the piezo voltage. Unfortunately, no output to report actual voltage but we do know the conversion between the two is 15x.

| NI USB-6002 Pin | Connects To                | Function                 |
|-----------------|-----------------------------|--------------------------|
| AO1             | MDT694 MOD IN             | Set piezo voltage        |
| AO GND          | MOD IN shield              | Ground                   |


> **Conversion**: 1 V = 15 V (Voltage limit = 150 V on MDT694)


### C. Frequency Measurement (Wavemeter 86120B)

- Connect via **GPIB-USB-HS** to PC
- Ensure the device is powered on and connected to the same PC running Python



## 2. Software Installation

### 2.1 Python Libraries
Install the required Python packages using pip:

```bash
pip install nidaqmx pyvisa matplotlib numpy
```

### 2.2 NI Drivers
You need both DAQ and VISA support from NI:

1. **NI-DAQmx Driver** (for USB-6002 DAQ)
   - Download: https://www.ni.com/en-us/support/downloads/drivers/download.ni-daqmx.html

2. **NI-VISA Runtime** (for GPIB communication)
   - Download: https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html

3. **NI MAX (Measurement & Automation Explorer)**
   - Included with NI-DAQmx or VISA install. Use it to verify devices like "Dev1".



## 3. Python Script Features

### 3.1 Set or Ramp Laser Current
```python
set_laser_current(150)              # Set 150 mA
ramp_laser_current(0, 250, 10)      # Ramp 0 to 250 mA over 10 seconds
```

### 3.2 Read Actual Current (from CTL OUT)
```python
current_mA = read_laser_current()   # Read actual output current
```

### 3.3 Connect and Query Wavemeter
```python
import pyvisa
rm = pyvisa.ResourceManager("@ni")
wavemeter = rm.open_resource("GPIB0::20::INSTR")
print(wavemeter.query("*IDN?"))     # Confirm connection
```

### 3.4 Read Frequency
```python
freq_Hz = float(wavemeter.query(":FETCH:SCALar:FREQuency?"))
print(f"Frequency: {freq_Hz/1e12:.6f} THz")
```

### 3.5 Read Multiple Frequency Lines
```python
response = wavemeter.query(":FETCH:ARRAY:SCALar:FREQuency?")
freqs_THz = [float(f)/1e12 for f in response.split(',') if f]
print("Detected lines (THz):", freqs_THz)
```


##  4. Real-Time Current vs Frequency Plot

You can sweep current and read frequency in parallel, storing (current, frequency) pairs and plotting them.

### Example Flow:
```python
for voltage in ramp:
    set_voltage(voltage)
    current = read_current()
    frequencies = read_all_frequencies()
    for f in frequencies:
        store(current, f)
plot(currents, frequencies)
```

This generates a **scatter plot** of laser frequency as a function of laser current, useful for characterizing mode hops or tuning behavior.


##  5. Notes and Tips

1. Always start with low current (50–100 mA) and set `ILIM` properly on the LDC205C front panel.
2. Use `time.sleep(0.2)` between steps to let wavemeter stabilize.
3. Confirm the device name (`Dev1`) with:
```python
import nidaqmx.system
print([d.name for d in nidaqmx.system.System.local().devices])
```
4. Use NI MAX to reset or rename DAQ devices if needed.
5. Ensure GPIB-USB-HS is recognized in NI MAX.


