# Sigma
A statically-typed, interpreted, brainrot based mix of python, c++, and COBOL.

## Purpose
I built this language to enhance my understanding of compiler design but for dummies. It was also to improve my regular expression skills `re`.

## Keywords/Syntax
- `BEGIN`: Always at the start of the program to begin the code
- `PERIOD`: Always at the end of the program to end the code
- `rob * from sigma`: Importing the interpreter. Similar to what `#include <stdio.h>` does in a C file

### Data Types
- `int`: Integer value
- `float`: Floating point value (decimal)
- `str`: String (including char)
- `bool`: Boolean value (true or false)

### Functions
- `tweak`: Initializing a function. Similar to `def` in python
- `call`: Used to call a function with its requested arguments

### Output
- `yap`: Used to print a value, or a variable to the console. Similar to `print` in python

### Code comments
- `//`: Single line or in-line comments
- `/*` and `*/`: Used to start and end multi-line comments

### Arrays
- `arrayzler<datatype> variableName = [comma-seperated-values]`: Initialize and define values in an array using this syntax
- `variableName[index] = value`: You can access values in an array using 0-indexing. The syntax is similar to that of pyhon.

## Usage
1) In order to use Sigma Language clone the github repo using the following command:
```bash
git clone https://github.com/kashsuks/Sigma
```
2) Followed by,

```bash
cd Sigma
```

3) Once you're in the `Sigma` directory, create a file with the `.sigma` extention and run it using the following command:
```bash
python sigma.py <filename.sigma>
```
4) Once the interpreter has processed the code, it will automatically display the result in the console. Enjoy :)

## License
This project is under the MIT License