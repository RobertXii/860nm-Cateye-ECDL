import nidaqmx
import numpy as np
import time
import matplotlib.pyplot as plt
import threading

mA_per_V = 50

def init_ao_task():
    task = nidaqmx.Task()
    task.ao_channels.add_ao_voltage_chan("Dev1/ao0", min_val=0.0, max_val=10.0)
    return task

def init_ldc_task():
    task = nidaqmx.Task()
    task.ao_channels.add_ao_voltage_chan("Dev1/ao0", min_val=-10.0, max_val=10.0)
    return task

def read_laser_current():
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("Dev1/ai0", min_val=0.0, max_val=10.0)
        voltage = task.read()
        current_mA = voltage * 50
        print(f"Read CTL OUT: {voltage:.3f} V to {current_mA:.2f} mA")

def set_voltage(voltage):
    with init_ao_task() as task: 
        task.write(voltage)
    print('Done')

def ramp_voltage(start_v, end_v, duration, steps = 100):
    voltages = np.linspace(start_v, end_v, steps)
    delay = duration / steps

    with init_ao_task() as task: 
        for v in voltages:
            task.write(v)
            time.sleep(delay)
    print('Done')

def set_laser_current(current_mA):
    voltage = current_mA/mA_per_V
    with init_ldc_task() as task:
        task.write(voltage)

def ramp_laser_current(start_mA, end_mA, duration, steps = 100):
    voltages = np.linspace(start_mA/mA_per_V, end_mA/mA_per_V, steps)
    # ramp_down = np.linspace(end_mA/mA_per_V, start_mA/mA_per_V, steps)
    # voltages = np.concatenate((ramp_up, ramp_down))

    # print(voltages)

    delay = duration / steps

    with init_ldc_task() as task: 
        for v in voltages:
            task.write(v)
            time.sleep(delay)
    print('Done')

# Threaded version wrapper
def start_ramp_thread(start_mA, end_mA, duration):
    thread = threading.Thread(target=ramp_laser_current, args=(start_mA, end_mA, duration))
    thread.start()
    return thread

ramp_thread = start_ramp_thread(10, 200, 10)

times = []
currents = []

plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [], '-o')
ax.set_xlabel("Time (s)")
ax.set_ylabel("Laser Current (mA)")
ax.set_title("Real-Time Laser Current")
ax.grid(False)
start_time = time.time()

with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("Dev1/ai0", min_val=0.0, max_val=10.0)
    while True:
        now = time.time() - start_time
        v = task.read()
        current = v * mA_per_V
        # Save data
        times.append(now)
        currents.append(current)
        # Update plot
        line.set_data(times, currents)
        ax.set_xlim(0, max(10, now))
        ax.set_ylim(0, max(10, 250))
        plt.pause(0.01)
        # Exit condition
        if now > 10:
            break
plt.ioff()
plt.show()

# set_voltage(3)
# ramp_voltage(1, 2, 10, steps=500)
# ramp_laser_current(-100,100,10)
# set_laser_current(100)
# read_laser_current()




