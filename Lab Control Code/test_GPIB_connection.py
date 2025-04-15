import pyvisa
import time

rm = pyvisa.ResourceManager()
wavemeter = rm.open_resource('GPIB0::20::INSTR')
wavemeter.timeout = 5000  # 5 seconds timeout

print("IDN:", wavemeter.query('*IDN?'))
print("POW:", wavemeter.query('FETCH:POW?'))  # Measure frequency
rm.visalib.set_debug_level(pyvisa.constants.DebugLevel.ON)



# print(wavemeter.query('MEAS:POW?'))  # Measure power