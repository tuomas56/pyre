from pyre.runtime import global_state, builtin_func
from pyre.objspace import PyreString, PyreObject, PyrePyFunc
from pyre.asteval import pyre_to_py_val
import sys

@builtin_func(global_state, 'print')
def _print(state, *args):
    print(*map(pyre_to_py_val, args))


@builtin_func(global_state, 'input')
def _input(state, prompt=PyreString('')):
    return PyreString(input(pyre_to_py_val(prompt)))


@builtin_func(global_state, 'quit')
def _quit(state):
    sys.exit()

class PyreBuffer(PyreObject):
	def __init__(self, value):
		super().__init__()
		self.eq_vars.append('value')
		self.value = value
		self.dict['read'] = PyrePyFunc(self.read)
		self.dict['write'] = PyrePyFunc(self.write)
		self.dict['close'] = PyrePyFunc(self.close)

	def read(self, n=-1):
		return PyreString(self.value.read(n))

	def write(self, bytes):
		self.value.write(bytes.value)
		return bytes

	def close(self):
		self.value.close()

@builtin_func(global_state, 'open')
def _open(state, filename, mode):
	return PyreBuffer(open(filename.value, mode.value))