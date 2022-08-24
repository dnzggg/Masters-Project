from STL import ast


def alw(phi, *, lo=0, hi=float('inf')):
    return ~env(~phi, lo=lo, hi=hi)


def env(phi, *, lo=0, hi=float('inf')):
    return ast.F(ast.Interval(lo, hi), phi)


def once(phi, *, lo=0, hi=float('inf')):
    return ast.O(ast.Interval(lo, hi), phi)


def historically(phi, *, lo=0, hi=float('inf')):
    return ~once(~phi, lo=lo, hi=hi)


def implies(x, y):
    return ~x | y


def xor(x, y):
    return (x | y) & ~(x & y)


def iff(x, y):
    return (x & y) | (~x & ~y)


def until(phi, psi):
    return ast.Until(phi, psi)


def timed_until(left, right, lo, hi):
    assert 0 <= lo < hi

    expr = env(right, lo=lo, hi=hi)
    expr &= alw(left, lo=0, hi=lo)
    expr &= alw(until(left, right), lo=lo, hi=lo)

    return expr


def since(phi, psi):
    return ast.Since(phi, psi)


def timed_since(left, right, lo, hi):
    # TODO: rewrite according to definition of since
    assert 0 <= lo < hi

    expr = env(right, lo=lo, hi=hi)
    expr &= alw(left, lo=0, hi=lo)
    expr &= alw(since(left, right), lo=lo, hi=lo)

    return expr
