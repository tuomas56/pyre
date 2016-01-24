##Syntax overview

A Pyre program consists of a single *expression*, which is 
evaluated when the program is run. In order to evaluate more than one 
expression per program, you must use *blocks.* Because of this,
whitespace does not matter, in fact, it is completely ignored by the
parser. As such, this:

```ruby
let 
x
=

10
```

Is equivalent to this:

```ruby
let x=10
```

An expression can be an assignment, a block, a conditional, a loop, 
a function definition, a try expression, a function call or an attribute access.

###Blocks

Blocks allow you to evaluate more than one expression.
The last expression in the block will be implicitly returned.
A `return` statement will exit a block, returning a value.

```ruby
do
	something
	something
	x #<- this is returned
end
```

```ruby
do
	something
	return y #<- the block exits here and returns y
	x
end
```

###Assignment

Assignments in Pyre are done via the `let` expression:

```ruby
let var = value
```

Pyre is scoped lexically, and variables only propagate
*down* scope, **not** up.

An assignment expression returns `value`.

###Conditionals

Conditionals in Pyre use the `if` block. This takes two expressions:
the condition and the expression to evaluate if it is true, as well
as an optional else statement.

```ruby
if cond expr
else elseexpr
```

This returns `expr` if `cond` is truthy, else it returns `elseexpr`
if this does not exist, it returns `None`.

###While loops

These take the form:

```ruby
while cond body
```

They return a list of values accumuated from executing 
`body` every iteration.

###Function calls

These take the traditional comma-seperated, bracketed syntax when there 
is one or more arguments. However, when there are no arguments, a exclamation
mark is used instead, like so:

```ruby
print!
```

###Attribute access

Uses the traditional dot-operator syntax:

```ruby
ident.attr
```

###Try expressions

Use the syntax:

```ruby
try expr
except eexpr
```

They return `expr` if no error occurred while evaluating it, and `eexpr` otherwise.
Crucially, `expr` *will* be evaluated both times.

###Function definitions

This uses the syntax:

```ruby
def (args) body
```

Where `args` is a comma-seperated list of argument names and `body` is the expression
to execute when the function is called, in terms of `args` and any variables up-scope.

It returns a function object, a first-class value.

###Module definition

This uses the syntax:

```ruby
module (names) body
```

Where `names` is a comma-seperated list of arguments names and `body` is the expression
to evaluate. The variables specified in `names` will be hoisted out of the local scope 
as attributes of the resulting module objects.