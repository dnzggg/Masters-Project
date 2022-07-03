from functools import singledispatch

from STL import ast


@singledispatch
def evaluate(phi, sig, time, t=0, points=500, time_period=20):
    print(type(phi))
    raise NotImplementedError


@evaluate.register(ast.AtomicPred)
def evaluate_ap(phi, sig, time, t=0, points=500, time_period=20):
    p = str(phi).strip("(").strip(")").replace(" ", "")
    if p[0] == "x":
        return float('inf') if sig[t] else -float('inf')
    elif p[0] == "t":
        return float('inf') if time[t] else -float('inf')


@evaluate.register(ast.AtomicExpr)
def evaluate_ae(phi, sig, time, t=0, points=500, time_period=20):
    p = str(phi).strip("(").strip(")").replace(" ", "")
    p = p.split("<")
    if p[0] == "x":
        return sig[t] - float(p[1])
    elif p[0] == "t":
        return time[t] - float(p[1])


@evaluate.register(ast.F)
def evaluate_f(phi, sig, time, t=0, points=500, time_period=20):
    a, b = phi.interval
    if t + b == float('inf'):
        next_ab = sig[t:]
    else:
        next_ab = sig[int(t + a * int(points/time_period)):int(t + b * int(points/time_period))]
    if len(next_ab) <= 0:
        return evaluate(phi.arg, sig, time, t)
    m = -float('inf')
    for j, n in enumerate(next_ab):
        temp = evaluate(phi.arg, sig, time, int(t + a * int(points/time_period) + j))
        if temp > m:
            m = temp
    return m


@evaluate.register(ast.F_)
def evaluate_f_(phi, sig, time, t=0, points=500, time_period=20):
    a, b = phi.interval
    if t - b == -float('inf'):
        prev_ab = sig[:t]
    else:
        prev_ab = sig[int(t - b * int(points/time_period)):int(t - a * int(points/time_period))]
    if len(prev_ab) <= 0:
        return evaluate(phi.arg, sig, time, t)
    m = -float('inf')
    for j, n in enumerate(prev_ab):
        temp = evaluate(phi.arg, sig, time, int(t - b * int(points/time_period) + j))
        if temp > m:
            m = temp
    return m


@evaluate.register(ast.Neg)
def evaluate_neg(phi, sig, time, t=0, points=500, time_period=20):
    temp = evaluate(phi.arg, sig, time, t)
    return -temp


@evaluate.register(ast.Or)
def evaluate_or(phi, sig, time, t=0, points=500, time_period=20):
    temp = [evaluate(a, sig, time, t) for a in phi.args]
    return max(temp)


@evaluate.register(ast.Until)
def evaluate_until(phi, sig, time, t=0, points=500, time_period=20):
    temp1 = evaluate(phi.arg1, sig, time, len(time) - 1)
    temp2 = evaluate(phi.arg2, sig, time, len(time) - 1)
    y_k_1 = min(temp1, temp2)
    for j in range(len(time) - 2, 0, -1):
        temp1 = evaluate(phi.arg1, sig, time, j)
        temp2 = evaluate(phi.arg2, sig, time, j)
        y_k_1 = max(min(temp1, temp2), min(temp1, y_k_1))
    return y_k_1
