import nidaqmx
import numpy as np
import time
import matplotlib.pyplot as plt
import threading

# ====== Configuration ======
DEVICE_NAME = "Dev1"
AO_CHANNEL = f"{DEVICE_NAME}/ao0"
AI_CHANNEL = f"{DEVICE_NAME}/ai0"
mA_per_V = 50  # Conversion factor from voltage to current


# ====== DAQ Setup Helpers ======
def init_ao_task(min_val=0.0, max_val=10.0):
    task = nidaqmx.Task()
    task.ao_channels.add_ao_voltage_chan(AO_CHANNEL, min_val=min_val, max_val=max_val)
    return task


def init_ai_task(min_val=0.0, max_val=10.0):
    task = nidaqmx.Task()
    task.ai_channels.add_ai_voltage_chan(AI_CHANNEL, min_val=min_val, max_val=max_val)
    return task


# ====== Laser Control ======
def read_laser_current():
    with init_ai_task() as task:
        voltage = task.read()
        current_mA = voltage * mA_per_V
        print(f"Read CTL OUT: {voltage:.3f} V → {current_mA:.2f} mA")


def set_voltage(voltage):
    with init_ao_task() as task:
        task.write(voltage)
    print(f"Set voltage: {voltage:.2f} V")


def ramp_voltage(start_v, end_v, duration, steps=100):
    voltages = np.linspace(start_v, end_v, steps)
    delay = duration / steps
    with init_ao_task() as task:
        for v in voltages:
            task.write(v)
            time.sleep(delay)
    print("Voltage ramp complete.")


def set_laser_current(current_mA):
    voltage = current_mA / mA_per_V
    with init_ao_task(min_val=-10.0, max_val=10.0) as task:
        task.write(voltage)
    print(f"Set laser current: {current_mA:.2f} mA")


def ramp_laser_current(start_mA, end_mA, duration, steps=100):
    voltages = np.linspace(start_mA / mA_per_V, end_mA / mA_per_V, steps)
    delay = duration / steps
    with init_ao_task(min_val=-10.0, max_val=10.0) as task:
        for v in voltages:
            task.write(v)
            time.sleep(delay)
    print("Current ramp complete.")


def start_ramp_thread(start_mA, end_mA, duration):
    thread = threading.Thread(target=ramp_laser_current, args=(start_mA, end_mA, duration))
    thread.start()
    return thread


# ====== Real-time time vs. current  ======
def log_and_plot_current(duration):
    times = []
    currents = []

    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot([], [], '-o')
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Laser Current (mA)")
    ax.set_title("Real-Time Laser Current")
    ax.grid(True)

    start_time = time.time()

    with init_ai_task() as task:
        while True:
            now = time.time() - start_time
            voltage = task.read()
            current = voltage * mA_per_V

            times.append(now)
            currents.append(current)

            line.set_data(times, currents)
            ax.set_xlim(0, max(duration, now))
            ax.set_ylim(0, max(350, current + 10))
            plt.pause(0.01)

            if now >= duration:
                break

    plt.ioff()
    plt.show()


# ====== Example Usage ======
if __name__ == "__main__":
    ramp_thread = start_ramp_thread(-100, 100, 5)
    log_and_plot_current(5)
