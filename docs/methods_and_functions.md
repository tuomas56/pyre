##Standard functions and methods

###Object objects

####Object#equals

Compares two objects.

####Object#apply

Takes a function and returns the object applied to that function.

####Object#str

Stringifies an object.

####Object#setattr

Sets an attribute on an object.

####Object#getattr

Gets an attribute of an object.

###Number objects

####Number#add

Adds two numbers, returning a third.

####Number#sub

Subtracts one number from another, returning a third.

####Number#mul

Multiplies one number by another, returning a third.

####Number#div

Divides one number by another, returning a third.

####Number#pow

Provides the exponentiation operation.

####Number#int

Truncates a number, returning its integer portion.

####Number#gt

Provides the 'greater than' relational operator.

####Number#lt

Provides the 'less than' relational operator.

####Number#and

Provides logical 'and'.

####Number#or

Provides logical 'or'.

####Number#not

Provides logical 'not'.

###String objects

####String#len

Returns a number containing the string's length.

####String#num

Attempts to parse the string as a number, raising ValueError if it can't.

####String#rep

Repeates the string n times.

####String#list

Returns a list containing the string's characters.

####String#concat

Adds to strings together

####String#split

Splits the string whenever the seperator appears.

###List objects

####List#reverse

Reverse the list, returning a new list.

####List#get

Gets the element at an index.

####List#set

Sets the element at an index.

####List#append

Appends an element to the list, returning it.

####List#pop

Pop one element from the end of the list, returning it.

####List#join

Convert the elements of the list to a string and join with the seperator.

####List#len

Gets the length of the list.

####List#map

Applies a function to each element in the array, returning the accumulated values.

####List#filter

Applies a function to each element in the array, returning only those for which the function returns a truthy value.

###Buffer objects

####Buffer#read

Reads from the buffer, if not argument is provided, everything is read.

####Buffer#write

Writes to the buffer.

####Buffer#close

Closes the buffer.

###True

A singleton value, exactly equal to 1.

###False

A singleton value, exactly equal to 0.

###quit!

Exits the program.

###print(values*)

Prints a some values, seperated by spaces.

###input(prompt?)

Displays a prompt and gathers the user's input.

###list(values*)

Constructs a list from its arguments.

###sum(list)

Sums an number list.

###import(name)

Imports a module, relatively. This replaces dots with slashes,
appends '.pyr' and then reads the file, evals it. Any variables not in
the global scope before will be hoisted into a module object as attributes. 
It behaves almost exactly like Python's import: everything will be evaluated.
It returns a module object like Node's require.

###object!

Constructs a blank object.