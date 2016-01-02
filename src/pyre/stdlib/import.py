from pyre.runtime import global_state, builtin_func
from pyre.asteval import pyre_eval
from pyre.objspace import PyreObject, PyreString
from pyre.parser import parse, tokenize

@builtin_func(global_state, 'import')
def _import(state, name):
	newstate = state.scope_down()
	with open(name.value.replace('.', '/') + '.pyr', 'r') as f:
		module = pyre_eval(parse(f.read()), newstate)
	return module