from functools import singledispatch
import numpy as np
import STL
import matplotlib.pyplot as plt


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


@singledispatch
def evaluate(phi, sig, time, t=0):
    print(type(phi))
    raise NotImplementedError


@evaluate.register(STL.ast.AtomicPred)
def evaluate_ap(phi, sig, time, t=0):
    p = str(phi).strip("(").strip(")").replace(" ", "")
    if p[0] == "x":
        return float('inf') if sig[t] else -float('inf')
    elif p[0] == "t":
        return float('inf') if time[t] else -float('inf')


@evaluate.register(STL.ast.AtomicExpr)
def evaluate_ae(phi, sig, time, t=0):
    p = str(phi).strip("(").strip(")").replace(" ", "")
    p = p.split("<")
    if p[0] == "x":
        return sig[t] - float(p[1])
    elif p[0] == "t":
        return time[t] - float(p[1])


@evaluate.register(STL.ast.F)
def evaluate_f(phi, sig, time, t=0):
    a, b = phi.interval
    if t + b == float('inf'):
        next_ab = sig[t:]
    else:
        next_ab = sig[int(t + a * int(points/time_period)):int(t + b * int(points/time_period))]
    if len(next_ab) <= 0:
        return evaluate(phi.arg, sig, time, t)
    m = -float('inf')
    for j, n in enumerate(next_ab):
        temp = evaluate(phi.arg, sig, time, t + a * int(points/time_period) + j)
        if temp > m:
            m = temp
    return m


@evaluate.register(STL.ast.F_)
def evaluate_f_(phi, sig, time, t=0):
    a, b = phi.interval
    if t - b - a == -float('inf'):
        prev_ab = sig[:t]
    else:
        prev_ab = sig[int(t - (b - a) * int(points/time_period)):int(t - a * int(points/time_period))]
    if len(prev_ab) <= 0:
        return evaluate(phi.arg, sig, time, t)
    m = -float('inf')
    for j, n in enumerate(prev_ab):
        temp = evaluate(phi.arg, sig, time, t - (b - a) * int(points/time_period) + j)
        if temp > m:
            m = temp
    return m


@evaluate.register(STL.ast.Neg)
def evaluate_neg(phi, sig, time, t=0):
    temp = evaluate(phi.arg, sig, time, t)
    return -temp


@evaluate.register(STL.ast.Or)
def evaluate_or(phi, sig, time, t=0):
    temp = [evaluate(a, sig, time, t) for a in phi.args]
    return max(temp)


@evaluate.register(STL.ast.Until)
def evaluate_until(phi, sig, time, t=0):
    temp1 = evaluate(phi.arg1, sig, time, len(time) - 1)
    temp2 = evaluate(phi.arg2, sig, time, len(time) - 1)
    y_k_1 = min(temp1, temp2)
    for j in range(len(time) - 2, 0, -1):
        temp1 = evaluate(phi.arg1, sig, time, j)
        temp2 = evaluate(phi.arg2, sig, time, j)
        y_k_1 = max(min(temp1, temp2), min(temp1, y_k_1))
    return y_k_1


robustness = []
for i, t in enumerate(time):
    robustness.append(evaluate(phi, sig, time, t=i))

print(phi)
plt.plot(time, sig, time, robustness, "--")
plt.xlim(0, 6)
plt.ylim(0, 5)
plt.xticks(np.arange(7, step=1))
plt.yticks(np.arange(0, 5, step=0.5))
plt.grid()
plt.show()
