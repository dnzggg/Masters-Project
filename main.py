import matplotlib.pyplot as plt
import numpy as np

import STL

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

points = 510

time_period = 6
time = np.linspace(0, 6, points, endpoint=True)
sig = [0, 2, 4, 2, 0, 2.1, 0]
temp = np.array([])
for i, s in enumerate(sig):
    try:
        b = np.linspace(sig[i], sig[i + 1], int(points/time_period))
    except IndexError:
        b = np.linspace(0, 0, int(points/time_period))
    if len(temp) < points:
        temp = np.concatenate((temp, b), axis=0)
sig = temp

x = STL.parse('(x<2)')
t = STL.parse('(t<1)')
phi = x.eventually().implies(t.always(lo=0, hi=1))


robustness = []
for i, t in enumerate(time):
    robustness.append(STL.evaluate(phi, sig, time, t=i, points=points, time_period=time_period))

print(phi)
plt.plot(time, sig, time, robustness, "--")
plt.xlim(0, 6)
plt.ylim(0, 5)
plt.xticks(np.arange(7, step=1))
plt.yticks(np.arange(0, 5, step=0.5))
plt.grid()
plt.show()
