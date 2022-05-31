# from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

# period = 500
# time = np.linspace(-1, 1, period, endpoint=False)
# _, sig = signal.gausspulse(time, fc=4, retquad=True)
# time = (time + 1) * period/2

points = 500

time_period = 20
time = np.linspace(0, 20, points, endpoint=True)
sig = [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, -1, 1, 1, 1, 1, 1, 1]
temp = np.array([])
for i, s in enumerate(sig):
    try:
        b = np.linspace(sig[i], sig[i + 1], int(points/time_period))
    except IndexError:
        b = np.linspace(1, 1, int(points/time_period))
    temp = np.concatenate((temp, b), axis=0)
sig = temp


# ¬(x ≥ 0.5) → once[0,1]historically[0,1](x ≥ 0.5)
# ¬(x ≥ 0.5) → once[0,1]¬once[0,10]¬(x ≥ 0.5)
robustness = []
for i, t in enumerate(time):
    signal = sig[i]
    next_1s = sig[i - int(points/time_period * 1):i]
    m = -float('inf')
    for j, n in enumerate(next_1s):
        next_next_1s = sig[i - int(points/time_period * 1) * 2 + j:i - int(points/time_period * 1) + j]
        m1 = -float('inf')
        for n1 in next_next_1s:
            temp1 = -(n1 - 0.5)
            if temp1 > m1:
                m1 = temp1
        temp = -m1
        if temp > m:
            m = temp
    if m == float('inf'):
        m = -m
    robustness.append(max(m, signal - 0.5))


# ¬(x ≥ 0.5) → eventually[0,1](x ≥ 0.5)
# robustness = []
# for i, t in enumerate(time):
#     signal = sig[i]
#     if not(signal >= 0.5):
#         next_1s = sig[i:i + int(points/time_period * 1)]
#         m = -float('inf')
#         for n in next_1s:
#             temp = n - 0.5
#             if temp > m:
#                 m = temp
#         robustness.append(m)
#     else:
#         robustness.append(1 - 0.5)


# ¬(x ≥ 0.5) → eventually[0,1]always[0,1](x ≥ 0.5)
# ¬(x ≥ 0.5) → eventually[0,1]¬eventually[0,1]¬(x ≥ 0.5)
# robustness = []
# for i, t in enumerate(time):
#     signal = sig[i]
#     if not(signal >= 0.5):
#         next_1s = sig[i:i + int(points/time_period * 1)]
#         m = -float('inf')
#         for j, n in enumerate(next_1s):
#             next_next_1s = sig[i + int(points/time_period * 1) + j:i + int(points/time_period * 1) * 2 + j]
#             m1 = -float('inf')
#             for n1 in next_next_1s:
#                 temp1 = -(n1 - 0.5)
#                 if temp1 > m1:
#                     m1 = temp1
#             temp = -m1
#             if temp > m:
#                 m = temp
#         robustness.append(m)
#     else:
#         robustness.append(signal - 0.5)

plt.plot(time, sig, time, robustness, "--")
plt.xlim(0, 20)
plt.ylim(-1.5, 1.5)
plt.xticks(np.arange(21, step=1))
plt.yticks(np.arange(-1.5, 1.51, step=0.5))
plt.grid()
plt.show()
