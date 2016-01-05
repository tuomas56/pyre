"""
(c) Tuomas Laakkonen 2015, under the MIT license.

pyre.runtime

An implementation of Pyre's builtin functions.
"""

from pyre.asteval import pyre_eval, pyre_to_py_val, State
from pyre.objspace import (
    PyreString,
    PyreNumber,
    PyreObject,
    Pyre_TRUE,
    Pyre_FALSE,
    PyrePyFunc,
    PyreList)
from pyre.parser import parse
from functools import partial
import sys

STDLIB_PY_MODULES = ['io', 'list', 'import', 'exts']
STDLIB_PYRE_MODULES = ['dict']

global_state = State()

def builtin_func(state, name, f=None):
    if f is None:
        return partial(builtin_func, state, name)
    else:
        state.locals[name] = (False, PyrePyFunc(partial(f, state)))
        return state.locals[name]

@builtin_func(global_state, 'eval')
def _eval(state, str):
    return pyre_eval(parse(str.value), global_state.scope_down())

@builtin_func(global_state, 'object')
def _object(state, *args):
    obj = PyreObject()
    for arg in args[0].values:
        obj._setattr(arg.values[0], arg.values[1])
    return obj

@builtin_func(global_state, 'error')
def _error(state, message):
    raise Exception(message)

@builtin_func(global_state, 'id')
def _id(state, *args):
    return args[0] if len(args) == 1 else args

global_state.locals['True'] = (False, Pyre_TRUE)
global_state.locals['False'] = (False, Pyre_FALSE)
global_state.locals['None'] = (None, None)

def load_stdlib():
    for mod_name in STDLIB_PY_MODULES:
         __import__("pyre.includes.%s" % mod_name)
    
    for mod_name in STDLIB_PYRE_MODULES:
        with open("%s/includes/%s.pyr" % (__file__[:-11], mod_name), "r") as f:
            pyre_eval(parse(f.read()), global_state)
