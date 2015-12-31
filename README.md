#Pyre

A Pythonic, expression-oriented language implemented in Python.

##Install

Standard install:

```
python3 setup.py install
```

If you are developing the module:

```
python3 setup.py develop
```

##Usage

```
usage: ipyre [-h] [-a {repl,stdin,load}] [-f FILE]

optional arguments:
  -h, --help                                        
  	show this help message and exit
  -a {repl,stdin,load}, --action {repl,stdin,load}  
  	what to execute: the repl, from stdin or load a file.
  -f FILE, --file FILE
  	the file to load
```

##The current state of Pyre

Done:

* While loops
* Error handling (all errors)
* Function defitions and calls
* Attribute access
* Variable assignment and scoping
* Blocks, return and break

Todo:

* For loops
* Generators
* Error handling (specific errors)
* Immutable and mutable variable modifiers
* Most of the Pyre object space
* Most of the Pyre standard library
* Making fundamental types available in Pyre
* Python interop