import matplotlib.pyplot as plt
import matplotlib
import numpy as np

import STL

# Online example
# points = 500
#
# time_period = 20
# time = np.linspace(0, 20, points, endpoint=True)
# sig = [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, -1, 1, 1, 1, 1, 1, 1]
# temp = np.array([])
# for i, s in enumerate(sig):
#     try:
#         b = np.linspace(sig[i], sig[i + 1], int(points/time_period))
#     except IndexError:
#         b = np.linspace(1, 1, int(points/time_period))
#     temp = np.concatenate((temp, b), axis=0)
# sig = temp
#
# x = STL.parse('~(x<0.5)')
# y = STL.parse('(x<0)')
# phi = x.implies(((~x).historically(lo=0, hi=1)).once(lo=0, hi=1))
# # t = STL.parse('(t < 10)')
# # phi = x.implies(y.always(lo=0, hi=1))

# Quantitative example
# points = 498
#
# time_period = 6
# time = np.linspace(0, 6, points, endpoint=True)
# sig = [0, 1, 3, 2, 1, 1]
# temp = np.array([])
# for i, s in enumerate(sig):
#     try:
#         b = np.linspace(sig[i], sig[i + 1], int(points/time_period))
#     except IndexError:
#         b = np.linspace(1, 1, int(points/time_period))
#     temp = np.concatenate((temp, b), axis=0)
# sig = temp
#
# x = STL.parse('(x<2)')
# phi = x.eventually(lo=0, hi=1)

# Slide example
points = 510

sig = dict()
time_period = 6
time = np.linspace(0, 6, points, endpoint=True)
sig1 = [0, 2, 4, 2, 0, 2.1, 0]
temp = np.array([])
for i, s in enumerate(sig1):
    try:
        b = np.linspace(sig1[i], sig1[i + 1], int(points / time_period))
    except IndexError:
        b = np.linspace(0, 0, int(points / time_period))
    if len(temp) < points:
        temp = np.concatenate((temp, b), axis=0)
sig['x'] = temp

x = STL.parse('(x<2)')
phi = x.eventually(lo=0, hi=1)

robustness = []
b_robustness = []
for i, t in enumerate(time):
    val = STL.evaluate(phi, sig, time, t=i, points=points, time_period=time_period)
    robustness.append(val)
    b_robustness.append(1 if val >= 0 else 0)

print(phi)
# plt.plot(time, sig, time, b_robustness, "--")
# plt.xlim(0, 20)
# plt.ylim(-1.5, 1.5)
# plt.xticks(np.arange(20, step=1))
# plt.yticks(np.arange(-1.5, 1.5, step=0.5))
# plt.grid()
# plt.show()

plt.rcParams['font.size'] = 22

plt.figure(figsize=(20, 7), dpi=100)
plt.axhline(y=2, color='black', linestyle='--')
plt.ylim(-0.01, 4.01)
plt.xlim(0, 6)
plt.xlabel("Time (t)")
plt.ylabel("Signal (x)")
plt.plot(time, sig['x'], "r")
plt.box(False)
plt.show()

plt.figure(figsize=(20, 7), dpi=100)
plt.axhline(y=0, color='black', linestyle='--')
plt.ylim(-0.01, 1.01)
plt.xlim(0, 6)
plt.xlabel("Time (t)")
plt.ylabel("Satisfaction Relation of F[0,1](x>2)")
plt.plot(time, b_robustness, "g")
plt.yticks([0, 1])
plt.box(False)
plt.show()

plt.figure(figsize=(20, 7), dpi=100)
plt.axhline(y=0, color='black', linestyle='--')
plt.ylim(-2.01, 2.01)
plt.xlim(0, 6)
plt.xlabel("Time (t)")
plt.ylabel("Robustness Degree Score of F[0,1](x>2)")
plt.plot(time, robustness)
plt.box(False)
plt.show()
