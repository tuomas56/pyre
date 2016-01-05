#The Pyre Tutorial

In this tutorial we are going to be making a simple guessing game.
This game will pick a random number and ask the user to guess it. It will then tell the user whether to guess higher or lower. The user gets a maximum of ten guesses.

This program can be divided into three parts:

* Picking a random number,
* Asking the user for input,
* Controlling how many times the user can guess,

##Basic Layout

First, let's create a file called *guessing_game.pyr*. Within this
we will create out program. Firstly, since a Pyre program can only be a simgle expression, we must create a block inside out program.

```ruby
do

end
```

Now, we need to create a main function that will be run when the program starts. And call it at the end of the do block.

```ruby
do
	let main = def () do

	end
	main!
end
```

Now we can move on to the first section of out project.

##Section 1 - Random Numbers

Pyre does not have a random number generator, so in order to do this we must use the Python's `random` module. This can be achieved through the `pyre.exts.pyinterop` extension. First we have to load this extension:

```ruby
	let pyi = loadex("pyre.exts.pyinterop")
```

We put imports and extensions in the main block of our program. Now we can import Python's random module.

```ruby
	let random = pyi.pyimport("random")
```

This now lets us pick random numbers using the `random.randint` and `random.randrange` functions.

##Section 2 - Safe User Input

Pyre provides the `input` primitive for gathering user input. However, using this on its own allows the user to enter inputs that make no sense in the context of our app, such as non-numeric characters.

To make `input` safer, we shall use a common pattern called the `get` pattern.
This takes a prompt, like `input` and a validation functions. `get` tries to get some user input, and then applies it to the validation function. If the function raises an error, `get` tries again. Otherwise, it returns the value returned by the validation function.

A simple implementation of this goes like this:

```ruby
	let get = def (prompt, validate)
		while True
			try
				return validate(input(prompt))
			except
				print("Invalid input!")
```

##Section 3 - Controlling The Number of Guesses

To do this, we need to use a similar method as we did in `get`. There are two different ways of doing this - `for` and `while` loops. This tutorial will use `for` loops (an implementation using `while` loops is left as an excercise to the reader.)

To do this we need to count down over the number of guesses the user has. If they guess correctly we need to end the loop. We need to set a flag, signaling whether the user managed to guess correctly. If the user guesses too high or too low, we must say so.

Here, the validation function for get is one that restricts input to numbers between 0 and 100.

We define all of this in a function, `guess_number`:

```ruby
	let guess_number = def (question, correct, guesses) do
		let validate = def (s) do
			let n = s.num!
			if n.gt(100).or(n.lt(0))
				error("Out of range!")
			n
		end
		for guess in range(guesses, 0, -1)
			let mut prompt = "You have ".concat(guess.str!)
				.concat(" guesses. ").concat(question)
			let mut n = get(prompt, validate)
			if n.equals(correct)
				return True
			else if n.gt(correct)
				print("Too low.")
			else if n.lt(correct)
				print("Too high.")
		False
	end
```

##Putting It All Together

All of this code goes into our `main` function.
Firstly, we must choose a random number:

```ruby
	let number = random.randrange(100)
```

Then, we must ask the user what number it is:

```ruby
	let success = guess_number("Guess the number: ", number, 10)
```

Then we must display whether the user won or not and ask them if they wish to play again:

```ruby
	if success
		print("Well done!")
	else
		print("You didn't guess correctly. The answer was ".concat(number.str!))

	let validate = def (s)
		if s.equals("y").or(s.equals("yes"))
			True
		else if s.equals("n").or(s.equals("no"))
			False
		else
			error("Not valid.")

	if get("Do you want to play again? ", validate)
		main!
```

The full source is available in *examples/guessing_game.pyr*.
