from pyre.runtime import global_state, builtin_func
from pyre.objspace import PyreString, PyreObject, PyrePyFunc, PyreBuffer
from pyre.asteval import pyre_to_py_val
import sys
import os

@builtin_func(global_state, 'print')
def _print(state, *args):
    print(*map(pyre_to_py_val, args))


@builtin_func(global_state, 'input')
def _input(state, prompt=PyreString('')):
    return PyreString(input(pyre_to_py_val(prompt)))


@builtin_func(global_state, 'quit')
def _quit(state):
    sys.exit()

@builtin_func(global_state, 'open')
def _open(state, filename, mode):
	return PyreBuffer(open(filename.value, mode.value))