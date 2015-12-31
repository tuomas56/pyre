"""
(c) Tuomas Laakkonen 2015, under the MIT license.

pyre.runtime

An implementation of Pyre's builtin functions.
"""

from pyre.asteval import pyre_eval, pyre_to_py_val, State
from pyre.objspace import (
    PyreString,
    PyreNumber,
    Pyre_TRUE,
    Pyre_FALSE,
    PyrePyFunc,
    PyreList)
from pyre.parser import parse
from functools import partial
import sys

global_state = State()


def builtin_func(state, name, f=None):
    if f is None:
        return partial(builtin_func, state, name)
    else:
        state.locals[name] = PyrePyFunc(partial(f, state))


@builtin_func(global_state, 'print')
def _print(state, *args):
    print(*map(pyre_to_py_val, args))


@builtin_func(global_state, 'input')
def _input(state, prompt=PyreString('')):
    return PyreString(input(pyre_to_py_val(prompt)))


@builtin_func(global_state, 'quit')
def _quit(state):
    sys.exit()

@builtin_func(global_state, 'list')
def _list(state, *args):
    return PyreList(list(args))

@builtin_func(global_state, 'sum')
def _sum(state, list):
    return PyreNumber(sum([x.value for x in list.values]))

global_state.locals['True'] = Pyre_TRUE
global_state.locals['False'] = Pyre_FALSE
