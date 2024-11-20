

First thing is a clear, concise statement of the problem in business language.

Do not take extra steps.
  Minimize transformation.

Identify the interfaces.
Work with the interfaces.
Between the interfaces is our code.
  Whatever happens there, do it in the fewest code statements possible.
  Measurable with McCabe cyclomatic complexity

There is a specific preferred sequence to use for solving any problem.
Solutions are preferred in the following order.
  - The base language
  - builtin modules of the base language
  - 3rd party modules of the base language
  - 3rd party code
  - 
  
Express the solution in the language of the interfaces as much as possible.


# ##################################

# pyopic

# This project: The Apiary
   fooeey.   Apiapy

# This project: pyapics (Python API clients)

- https://apiary.io    Oracle
- https://pypi.org/project/apiary/   0.0.8 and moribund ???? yes, 9 years
  apparently a client to the above.
  clone of some Ruby tool
  apiary-client

- https://github.com/pepsipu/PyAPI
    crude and moribund 6 years
- https://pypi.org/project/pyapi/     no repo
   moribund 8 years
- https://pyapi-server.readthedocs.io/en/latest/   active and appears useful
- https://pypi.org/project/pyapi-client/           Sep 2024
- https://github.com/berislavlopac/pyapi-client     "   "
         2 years old
https://pypi.org/project/pyapic/   moribund 4 years

pyapix

- 
- 
- 

### Problem Statement

Call any endpoint of any API having an OpenAPI document. 
Validate endpoint input.

### Tools

- Python
    - json, jsonschema, jsonref
    - httpx


### Solution strategy

The OpenAPI file contains the names of all endpoints and verbs along with
parameter information.  

#### Convert the OpenAPI file into a Python data structure

Parsing json is non-trivial so we use the builtin `json` module.

#### Extract relevant information

Straightforward using the Python language.

Expressing this document in Python is a one-liner so do
that.  Extracting the information from the resulting Python data structure is
straightforward.


# Unstated assumptions 

The industry standard usually makes two erroneous assumptions.

- code quality is not important
- everything must be done with classes

Both are absurd.  Sometimes code quality is not important.  But the more
demanding the tasks performed, the more important it becomes to use high quality
code.
Sometimes the OO paradigm is best and sometimes not.
btw, sometimes we can do both.

Another bad assumption, when working with JSON data, is that the JSON must be
converted to OO classes.


# Levels

The low-level interface has the goal of being a MVR of the OpenAPI document. 

- MVR Minimum Viable Representation

The high-level interface provides user-friendly dot notation for the same.



