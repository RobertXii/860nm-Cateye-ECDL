# Laser Current and Frequency Control System

This project sets up a complete experimental control system for a tunable laser using:

- Thorlabs **LDC205C** (laser current controller)
- Thorlabs **MDT694** (piezo voltage controller)
- National Instruments **USB-6002 DAQ** (for analog control and monitoring)
- HighFinesse **WS/7 8395** (for measuring absolute laser frequency)
- Keysight **86120B Wavemeter** (can't pull frequency data to computer, so I switched to HighFinesse WS/7 8395)
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
| HighFinesse WS/7 8395 | Optical frequency/wavelength meter|
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

2. **NI-VISA Runtime** (for GPIB communication, but since we are not using the old wavemeter, can skip this)
   - Download: https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html

3. **NI MAX (Measurement & Automation Explorer)**
   - Included with NI-DAQmx or VISA install. Use it to verify devices like "Dev1".



## 3. Python Script Features

### 3.1 Set or Ramp Laser Current
```python
set_laser_current(150)              # Set 150 mA
ramp_laser_current(0, 250, 10)      # Ramp 0 to 250 mA over 10 seconds
```
See daq_control_Robert.py

### 3.2 Read Actual Current (from CTL OUT)
```python
current_mA = read_laser_current()   # Read actual output current
```
See daq_control_Robert.py

### 3.3 Connect and Query Wavemeter (Not Working)
```python
import pyvisa
rm = pyvisa.ResourceManager("@ni")
wavemeter = rm.open_resource("GPIB0::20::INSTR")
print(wavemeter.query("*IDN?"))     # Confirm connection
```
See test_GPIB_connection

### 3.4 Read Frequency
```python
freq_Hz = float(wavemeter.query(":FETCH:SCALar:FREQuency?"))
print(f"Frequency: {freq_Hz/1e12:.6f} THz")
```
See daq_control_Robert.py

### 3.5 Scan Current/Voltage vs. Frequency
```python
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

```
See feedforward_piezo_voltage_vs_current.py

### 3.6 GUI For Piezo Voltage Control With Feedforward
See feed_forward_GUI.py


##  4. Notes and Tips

1. Always start with low current (50–100 mA) and set `ILIM` properly on the LDC205C front panel.
2. Use `time.sleep(0.2)` between steps to let wavemeter stabilize.
3. Confirm the device name (`Dev1`) with:
```python
import nidaqmx.system
print([d.name for d in nidaqmx.system.System.local().devices])
```
4. Use NI MAX to reset or rename DAQ devices if needed.
5. Ensure GPIB-USB-HS is recognized in NI MAX.
6. When getting frequency from HighFinesse wavemeter, use getFrequencyNum(x, 0) with channel x = 3 or 4

By trials, a good combination of paramters are: 300mA diode current; 8.05 kilo Ohm thermoresistor; arb. piezo voltage. It's observed that when tunning laser diode alone, lasing frequency jumps in discrete steps every 4mA (0.08V DAQ input signal) with frequency inteval around 1.5GHz; when tunning the piezo voltage, the frequency changes smooothly and hops every 15V (1V DAQ input signal). piezo_voltage_vs_frequency_scan.py, current_vs_frequency_scan.py, and feedforward_piezo_voltage_vs_current.py allows scan across different variables, and if everthing set up, they produce the following images:

[current vs frequency.pdf](https://github.com/user-attachments/files/19769281/current.vs.frequency.pdf)
[piezo voltage vs frequency.pdf](https://github.com/user-attachments/files/19769282/piezo.voltage.vs.frequency.pdf)
[piezo voltage with feedforward vs frequency.pdf](https://github.com/user-attachments/files/19769283/piezo.voltage.with.feedforward.vs.frequency.pdf)



