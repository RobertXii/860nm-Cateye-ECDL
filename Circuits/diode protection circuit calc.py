# Bode plot for the ladder RC–L–R network shown in your sketch
# Topology (left to right):
#   Vout node ── C1 to GND ── L ── node A ── C2 to GND ── R ── Vin
# Output is the voltage across C1 (Vout). We plot H(jw) = Vout/Vin.

import numpy as np
import matplotlib.pyplot as plt

# --------- User parameters ----------
L  = 100e-6    # H
C1 = 1e-9      # F  (left capacitor; output across this)
C2 = 1e-6      # F  (shunt at node A)
R  = 1.6       # ohm (series from Vin to node A)

f_min = 1e2    # Hz
f_max = 1e7    # Hz
npts  = 2000   # points per decade (log-spaced total points)
# ------------------------------------

# Frequency axis
f = np.logspace(np.log10(f_min), np.log10(f_max), npts)
w = 2*np.pi*f
j = 1j

# Element impedances
Zc1 = 1/(j*w*C1)
Zc2 = 1/(j*w*C2)
ZL  = j*w*L

# Subnetworks
Zs = ZL + Zc1                # series of L and C1
Zp = (Zc2 * Zs) / (Zc2 + Zs) # parallel of C2 with (L + C1) at node A

# Voltage division
Va_over_Vin = Zp / (R + Zp)  # Vin to node A
Vc1_over_Va = Zc1 / Zs       # node A to Vout (across C1)
H = Va_over_Vin * Vc1_over_Va

# Magnitude (dB) and phase (deg)
mag_db = 20*np.log10(np.abs(H))
phase_deg = np.unwrap(np.angle(H)) * 180/np.pi

# ---- Combined magnitude and phase plots ----
fig, (ax_mag, ax_phase) = plt.subplots(2, 1, figsize=(8, 7), sharex=True)

# Magnitude subplot
ax_mag.semilogx(f, mag_db)
ax_mag.set_ylabel("Gain |H(jω)| (dB)")
ax_mag.set_title("Magnitude: Vout/Vin (across C1)")
ax_mag.grid(True, which="both", linestyle=":", linewidth=0.6)
ax_mag.set_ylim(-20, 20)

# Phase subplot
ax_phase.semilogx(f, phase_deg)
ax_phase.set_xlabel("Frequency (Hz)")
ax_phase.set_ylabel("∠H(jω) (deg)")
ax_phase.set_title("Bode Phase: Vout/Vin (across C1)")
ax_phase.grid(True, which="both", linestyle=":", linewidth=0.6)
ax_phase.set_ylim(-360, 50)

plt.tight_layout()
plt.savefig("original_diode_protection_circuit_bode_plot.pdf", dpi=300)
plt.show()
