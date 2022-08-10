from functools import singledispatch

from STL import ast
import re


@singledispatch
def evaluate(phi, sig, time, t=0, points=500, time_period=20):
    print(type(phi))
    raise NotImplementedError


@evaluate.register(ast.AtomicPred)
def evaluate_ap(phi, sig, time, t=0, points=500, time_period=20):
    p = str(phi).strip("(").strip(")").replace(" ", "")
    return float('inf') if sig[p[0]][t] else -float('inf')


@evaluate.register(ast.AtomicExpr)
def evaluate_ae(phi, sig, time, t=0, points=500, time_period=20):
    p = str(phi).strip("(").strip(")").replace(" ", "")
    p = p.split("<")
    return sig[p[0]][t] - float(p[1])


@evaluate.register(ast.F)
def evaluate_f(phi, sig, time, t=0, points=500, time_period=20):
    p = re.sub(r"(\d)+(\.\d)?,((\d)+(\.\d)?|inf)", "", str(phi))
    p = p.strip("F").strip("[").strip("]").strip("~").strip("(").strip(")").replace(" ", "")
    p = p.split("<")
    a, b = phi.interval
    if t + b == float('inf'):
        next_ab = sig[p[0]][t:]
    else:
        next_ab = sig[p[0]][int(t + a * points/time_period):int(t + b * points/time_period)]
    if len(next_ab) <= 0:
        return evaluate(phi.arg, sig, time, t)
    m = -float('inf')
    for j, n in enumerate(next_ab):
        temp = evaluate(phi.arg, sig, time, int(t + a * points/time_period + j))
        if temp > m:
            m = temp
    return m


@evaluate.register(ast.O)
def evaluate_f_(phi, sig, time, t=0, points=500, time_period=20):
    p = re.sub(r"(\d)+(\.\d)?,((\d)+(\.\d)?|inf)", "", str(phi))
    p = p.strip("O").strip("[").strip("]").strip("~").strip("(").strip(")").replace(" ", "")
    p = p.split("<")
    a, b = phi.interval
    if t - b == -float('inf'):
        prev_ab = sig[p[0]][:t]
    elif int(t - b * points/time_period) < 0:
        if int(t - a * points/time_period) < 0:
            prev_ab = []
        else:
            prev_ab = sig[p[0]][:int(t - a * points/time_period)]
    else:
        prev_ab = sig[p[0]][int(t - b * points/time_period):int(t - a * points/time_period)]
    if len(prev_ab) <= 0:
        return evaluate(phi.arg, sig, time, t)
    m = -float('inf')
    for j, n in enumerate(prev_ab):
        if t - b * int(points/time_period) < 0:
            temp = evaluate(phi.arg, sig, time, j)
        else:
            temp = evaluate(phi.arg, sig, time, int(t - b * points/time_period + j))
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
