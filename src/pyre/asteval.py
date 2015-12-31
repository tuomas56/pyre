"""
(c) Tuomas Laakkonen 2015, under the MIT license.

pyre.asteval

A simple implementation of pyre_eval and the surrounding machinery
which directly evaluates the AST.

DEPRECATED:
Will eventually be replaced by a VM and bytecode compiler.
"""

from pyre.parser import (
    parse,
    Name,
    Call,
    Attr,
    IfExpr,
    Number,
    String,
    Block,
    VarExpr,
    WhileExpr,
    DefExpr,
    TryExpr,
    ReturnExpr,
    BreakExpr,
    ForExpr)
from pyre.objspace import *
from functools import partial
import inspect

class StateDict:

    def __init__(self, parent):
        self.items = {}
        self.parent = parent

    def __getitem__(self, name):
        if name in self.items:
            return self.items[name]
        else:
            return self.parent[name]

    def keys(self):
        return self.parent.keys()

    def update(self, other):
        for k, v in other.items():
            self[k] = v

    def __setitem__(self, name, value):
        if name in self.parent.keys():
            self.parent[name] = value
        else:
            self.items[name] = value


class State:

    def __init__(self, parent=None, locals=None):
        self.parent = parent
        self.locals = locals if locals is not None else StateDict({})

    def scope_down(self):
        return State(self, StateDict(self.locals))

    def copy(self):
        return State(self, self.locals.copy())


def pyre_call(expr, args):
    return pyre_getattr(expr, '__call__')(*args)


def pyre_hasattr(expr, attr):
    return attr in expr.dict


def pyre_truthy(expr):
    if isinstance(expr, PyreNumber) and expr.value == 0:
        return False
    return True


def pyre_getattr(expr, attr):
    if pyre_hasattr(expr, '__getallattr__'):
        return pyre_call(expr.dict['__getallattr__'], attr)
    elif pyre_hasattr(expr, attr):
        return expr.dict[attr]
    elif pyre_hasattr(expr, '__getattr__'):
        return pyre_call(expr.dict['__getattr__'], attr)
    else:
        raise AttributeError(
            'object "%s" has no attribute "%s"!' % (expr, attr))


def pyre_to_py_val(expr):
    if isinstance(expr, PyreNumber):
        return expr.value
    elif isinstance(expr, PyreString):
        return eval('"%s"' % expr.value)
    elif isinstance(expr, (PyreList)):
        return [pyre_to_py_val(x) for x in expr.values]
    elif isinstance(expr, (PyrePyFunc)):
        return expr.dict['__call__']


class BreakError(Exception):
    pass


class ReturnError(Exception):

    def __init__(self, value):
        self.value = value


def pyre_eval(expr, state):
    if isinstance(expr, Name):
        try:
            return state.locals[expr.value]
        except:
            raise NameError('No such variable "%s"!' % expr.value)
    elif isinstance(expr, Call):
        args = [pyre_eval(arg, state) for arg in expr.args]
        stem = pyre_eval(expr.value, state)
        return pyre_call(stem, args)
    elif isinstance(expr, Attr):
        return pyre_getattr(pyre_eval(expr.value, state), expr.name)
    elif isinstance(expr, IfExpr):
        cond = pyre_eval(expr.cond, state)
        if pyre_truthy(cond):
            return pyre_eval(expr.body, state)
        elif expr.elsebody is not None:
            return pyre_eval(expr.elsebody, state)
    elif isinstance(expr, Number):
        return PyreNumber(expr.value)
    elif isinstance(expr, String):
        return PyreString(expr.value)
    elif isinstance(expr, Block):
        try:
            vals = [None] + [pyre_eval(e, state) for e in expr.value]
        except ReturnError as e:
            return e.value
        return vals[-1]
    elif isinstance(expr, WhileExpr):
        result = []
        while pyre_truthy(pyre_eval(expr.cond, state)):
            try:
                result.append(pyre_eval(expr.body, state))
            except BreakError:
                break
            except ReturnError as e:
                return e.value
        return PyreList(result)
    elif isinstance(expr, ForExpr):
        result = []
        newstate = state.scope_down()
        for x in pyre_call(pyre_getattr(pyre_eval(expr.expr, state), '__iter__'), []):
            newstate.locals[expr.var.value] = x
            result.append(pyre_eval(expr.body, newstate))
        newstate.locals.parent.update(newstate.locals.items)
        state.locals = newstate.locals.parent
        return PyreList(result)
    elif isinstance(expr, DefExpr):
        def _wrapper(*args):
            if len(args) > len(expr.args):
                raise TypeError('Too many arguments supplied!')
            args = dict(zip(expr.args, args))
            if len(args) < len(expr.args):
                raise TypeError('Not enough arguments supplied!')
            dstate = state.scope_down()
            dstate.locals.update(args)
            try:
                return pyre_eval(expr.body, dstate)
            except ReturnError as e:
                return e.value
        return PyrePyFunc(_wrapper)
    elif isinstance(expr, TryExpr):
        try:
            return pyre_eval(expr.body, state)
        except ReturnError:
            raise
        except BreakError:
            raise
        except:
            return pyre_eval(expr.exceptbody, state)
    elif isinstance(expr, BreakExpr):
        raise BreakError()
    elif isinstance(expr, ReturnExpr):
        raise ReturnError(pyre_eval(expr.value, state))
    elif isinstance(expr, VarExpr):
        state.locals[expr.var] = pyre_eval(expr.value, state)
        return state.locals[expr.var]
    else:
        raise TypeError("Can't eval object of type '%s'!" %
                        type(expr).__name__)
