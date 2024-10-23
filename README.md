# readme


A tool for quickly creating high quality API clients (SDKs).  Initial target APIs are
those defined in Swagger/OpenAPI.

First step is to read swagger / OpenAPI files.
These files are in json/yaml.
We shall take the things we find there and represent them as data.
DONE

Next step is to validate data against the swagger.  The tricky part is getting
references.  Worthwhile because it keeps us in the original data format.
DONE

Call the APIs.
DONE

Other tasks present themselves as we go.  Navigating json data is tedious
without good tools so we create the tools as we go.


# How to do it?

We follow principles of ...

- the Unix Philosophy
- the Agile Manifesto
- good code
- bad code
- etc

There are important factors that are routinely ignored in typical Python
programming.  Two of these include...

- do not duplicate effort
- do not transform without justification

If someone else has already defined important data we will not repeat that
effort.  Likewise, when we receive data we will not transform it without a good
reason.  "our programmers like Pydantic" (or other xxx) is not a good reason.

Our target users are people who understand the swagger.  The goal is to remove
the need for the programmer between the data analyst and the data.

Our system will be intuitive for data analysts.

### You

You are familiar with the API.  Are comfortable reading the Swagger Doc
description.  Are comfortable using Postman to access the API.

If you are familiar with either the Swagger Doc or Postman, my code will look
familiar. 


### Why does it look familiar?

Because the three of us...

- Swagger Doc
- Postman
- me

have noticed that an API is all about interacting with (endpoint, verb) pairs.
The code is written in a way to keep the focus on that.


### Similar tools

- Swagger Doc
- Postman

The project takes an approach similar to both of the above.  You get access to
the (endpoint, verb) with the ability to send and recieve data.


### Drinking glasses

Square drinking glasses (and other exotic shapes) are fun to look at, and great
fun for the designer, but not ergonomic.
Same for DAOs.  It's not the shape of your data.

exotic...

- square
- flower shape, flaring out at the top.
- tall and narrow
- short and squat

### Needless transformation

xxxx

### Translation

From json to DAO.  Translation is an interesting programming problem.  But if it
is not your core business, why are you doing it?
There are many things one can say about DAO.  There is one thing I can say for
certain about it.  It is not solving your business problem.

The "best practice" in software engineering is to begin with the assumption that
the data needs to be translated into DAO.
This assumption is unwarrented.
                   ridiculous
                   absurd
                   unexamined
Assumptions in code should be stated explicitly.
Caveat.  Sometimes DAO is a good approach, or even ideal.  Explain...


### More...


We pull data from swagger and use it.  Unfortunately, swagger files often
contain errors so a pre-processing step(s) is required.

Tests are written BEFORE code.  When tests are written after code the bugs
become baked into the tests.  Fooey on that!

Using swagger as data has multiple benefits.

- no duplication of effort that went into swagger defs
- a record of swagger errors

We do not have to define our data if someone else (the swagger author) has
already done it.  This is a huge benefit.

Our tests will reveal any errors in the swagger.  Errors are corrected in the
pre-processing step.  Errors also generate bug reports to the swagger maintaner.
Given the option of multiple swagger sources we go for the one with fewest
errors and best responsiveness to bug reports.

Swagger is not the only acceptable data source.  It is a good data source
because it is a well-defined json/yaml representation with good documentation.
There are plenty of other good options, for example botocore.  botocore is
a well thought-out system.
The important thing is to have a well-defined, slowly changing interface.  If we
have that we can write code quickly to leverage the API.  If we have competition
that prefers the xxx/marshmallow/pydantic approach of manually defined Python
classes, so much the better.  We will run circles around them.  (read Paul
Graham).

### Our motivation

- https://agilemanifesto.org
- https://en.wikipedia.org/wiki/Unix_philosophy
- https://github.com/boto/botocore
- https://www.paulgraham.com
- https://d3js.org

d3js is a javascript library that provides a minimal wrapper around SVG.  If you
understand SVG, d3js will make a lot of sense to you.

- https://aframe.io/docs/1.6.0/introduction/

Aframe is a javascript library around (WebGL?).


### APIs with OpenAPI doc

- https://www.weather.gov/documentation/services-web-api
- https://api.weather.gov/openapi.json NWS   OpenAPI v 3.0
- https://developer.osf.io  open science
- https://apis.guru/api-doc/    List of OpenAPI services


#### APIs w/o swagger found
- https://open-meteo.com  weather    NO swagger file found
- https://info.arxiv.org/help/api/user-manual.html  no swagger
- https://newton.vercel.app   no swagger.   symbolic math


#### The competition

- https://github.com/WxBDM/nwsapy/blob/master/nwsapy/
  a worthy competitor.

- google:  nws api client       for useful links

### Our tools

- https://github.com/OAI/OpenAPI-Specification
- https://swagger.io/specification/
- https://docs.python.org/3/library/json.html
- https://daringfireball.net/projects/markdown/
- https://github.com
- https://json-schema.org
- https://json-schema.org/understanding-json-schema
- https://developer.mozilla.org/en-US/docs/Web/API/
- https://github.com/APIs-guru/openapi-directory
- https://github.com/public-apis/public-apis
- python hypothesis for auto-generating data


-----------------------------

- https://www.postman.com
- https://pypi.org/project/PyYAML/
- https://jinja.palletsprojects.com/en/3.1.x/

Jinja does for text strings, something like what d3js does for svg.  A minimal
way of inserting data into a fixed string.

### Not our tools

There is nothing wrong with the below tools.  If we have reason, we will use
them.  But it requires justification.  Unfamiliarity with functional programming
in Python is not justification.  "Everyone does it that way." is not
justification.

- https://docs.pydantic.dev/latest/
- https://marshmallow.readthedocs.io/en/stable/

These tools tend to make life easy for programmers and their managers.  Most
programmers are familiar with the approach.  It's not too demanding and provides
a simple, rigid interface.  Our goal is to make life easy for the data analyst
or manager who is interested in exploring the interface in real time without
waiting for programmers to define their options for them.

The code we write will demand more from the programmer but will be far more
compact than code written using the above approach.  Also far more flexible.
The data analyst will thank us.



### TODO

- hyperlinks
- code
- data source

### Potential data sources

- https://documents.worldbank.org/en/publication/documents-reports/api
- https://fred.stlouisfed.org/docs/api/fred/
- https://opensource.fb.com/projects/
- https://developer.x.com/en/docs/x-api

### swagger petstore

We are currently using the Petstore data from the swagger docs.

- https://petstore.swagger.io/v2/swagger.json


### Interfaces / handoffs / context switch / complexity

Cognitive load is not a joke.


### Functional programming in Python

Python has almost all functional programming features of Lisp, except macros.

To get a handle on functional programming in Python, decorators are a good
starting point.  The coder who has a solid understanding of decorators is well
on the way to having a good grounding in functional programming in Python.
There are several things to consider.

- basic decorator
- class-based decorator

The first thing with decorators is to understand the simplest possible version.
Then we can move on to class-based decorators.   One could gain a solid
understanding without ever using class-based decorators but they are good to
know about and understand.  One could make the argument that a class-based
decorator is sort of like object-oriented Perl or a dog walking on its hind
legs.  You can do it but it is ugly and does not work well.  So feel free to
skip class-based decorators at first but come back and figure them out later.

Parameterized decorators, on the other hand, are essential for a good
understanding.  Decorators (and particularly parameterized decorators) are
a special case of Python functional programming.  But once you really understand
parameterized decorators you will begin to understand where functional
programming can be used most effectively.

Python is a multi-paradigm language.  It's support for functional programming is
solid and baked in.  It's not going away.  Treating Python as a strictly OO
language is like sawing off one of the legs of your three-legged stool.
You miss out on a lot.


# Glossary

- DAO: data in object drag
- WIP: work in progress
- SDK: aka client

# FAQ

- Why not use DAOs?

Because DAOs are

- tedious to write
- error prone
- not the original data
- undocumented


#### what is the problem?

Q. What is the problem with most Python code today?
A. It is written for the convenience of the original programmer.  The ultimate
   programmer/user is not considered.

Q. So what?
A. If it's throwaway code, then NP.  But if the code continues getting used,
   problems accumulate.

Q. How to fix?
A. Start at the end and work backwards.  From POV of end user/programmer.


#### Target User

- intelligent
- some programming experience / comfort
- issue aware re the API   (possibly the swagger file but probably not).


#### Another swagger API

- https://api.obis.org/obis_v3.yml
- https://api.obis.org/
- server https://api.obis.org/obis_v3



#### The wrong question.

A common question on StackOverflow...

"""
I have a complex json document and want to convert it into Python data.
How can I do that?
"""

¡¡¡¡News Flash!!!!!

json data IS Python data.

Converting json data into OO does not reduce essential complexity.
In general, json data is dense.
Converting to OO INCREASES complexity, usully ELIMINATING information at the
same time.


Sancho Prize for Ura.   For beating both Ozeki.
If he gets Katchikoshi.

json == essential complexity.
Learn to deal with it.
conversion => complexity, opportunity for translation errors


#### Industry Standzzrd

blha blah


#### but Grossly Mistaken

been reading Franklin

- you doon't change it and
- you don't thrhow it away


#### A step in the right direction

Make your code pass this test.

def test(self):
    self.to_dict() == self  == dict(self)`
    self.to_dict() is self  is dict(self)`
    # dict(self) keeps us honest
    # altering the `dict` function not allowed.


#### Javathonic / Simplistic

Simplistic == sadly True 
Ironic
Adding syllables does not make for a better word.


class-based translation is a simplification / approximation of the actual
problem.  Then the business problem is solved on this simplified version and
then the data re-transformed back to original (or some other) format, and we
hope the actual problem is solved.  Often it is almost solved.  Edge cases left
uncovered, etc.


#### For Managemnt Eyes Only

Red flags for simplistic code.

- lots of to_dict methods
- validation of an approximation
- x


#### This is not a joke

It is treated as a joke by industry standard but.
Energy given to translation/simplification is energy NOT given to solving the
business problem.

The difference is measurable.

- McCabe cyclomatic complexity
- at the computational level.   (not green)

It simply makes more operations by the computer.  This adds up.  Not green.

btw.  I bet there is a way to measure information density of json data vs class
data.  And I'm betting it turns out json is more dense.  So we transform dense
data in a simplistic way.  Solve the problem using the simplistic
representation, and then re-translate.   ugh.
I propose to work with the actual data instead.

Yes, it's a bit more difficult.  But the advantages accrue as the business
problems get more demanding.


#### When NOT to use it

- fast-changing API
- small projects
- one-off projects
- throw-away code
- short-term projects

#### When to use it

- multiple APIs
- solving unknown problems
- solving problems you have not thought of yet

#### message to management

The simplistic approach constrains your thinking.
Your programmers tell you it takes a long time to solve simple problems and it
is not true.

industry standard claim:  Working with the original incoming data is too hard.
We have to simplify before solving.

fact:  Working with json data is not so hard if you actually use the language
instead of writing javathonic code.

Pythonic is NOT automatically using classes to solve every problem.
Pythonic means solving the problem in the fewest possible code statements.
Pythonic means using the power of the Python language, not writing Java code in
Python.

- not reinventing the wheel

### The Industry Standard is Simplistic

And that is a 

- slow
- clumsy
- tedious
- error-prone
- labor-intensive

way of solving problems.

#### The other way

When you do this, the programmer ends up speaking about objects that
are familiar to a person who understands the API.  People such as

- manager
- data analyst

Streamlines the problem solving process.

### Do not try to guess what they/you will need

you will get it wrong.

### Jupyter Notebook

do it.

### Advice

Put the logic into data.  Pero como de costumbre hay mas a pensar.



I like this distinction from wikipedia [1] "Anything that is a process or
procedure is business logic, and anything that is neither a process nor
a procedure is a business rule." Meaning constraints and the model represent
business rules.
1. https://en.wikipedia.org/wiki/Business_logic


I find that there are very few things related to programming that don't
constitute an interface in some way,


Here's what I'm talking about...

https://swizec.com/blog/how-to-think-of-your-business-logic-as-data/

!!!!!!!!!!!!!!!!!


### Things to watch

- https://htmx.org  Interactivity w/o javascript
- https://opensource.fb.com/projects/ Meta Opensource
- https://jinja.palletsprojects.com/en/3.1.x/templates/
   how to do templates

### Interesting reading
- https://blog.postman.com/what-is-json-schema/
- https://www.semanticarts.com/data-centric-how-big-things-get-done-in-it/
- https://www.semanticarts.com/the-data-centric-revolution-best-practices-and-schools-of-ontology-design/


### Competition
- https://openapi-core.readthedocs.io/en/latest/extensions.html
- https://github.com/commonism/aiopenapi3
- https://github.com/wy-z/requests-openapi
- 
- 


### Caveat

jsonschema cannot do everything.


### Outsourcing the thinking.

We cannot do everything from first principles.  This is the whole point of high
level languages.  But we should not outsource our fundamental tasks eg
validation.
Maintain the data in its original representation unless there is a compelling
business need.
And do not discard information unless there is a business need.
eg validation info in the OpenAPI file.

"we use Pydantic for validation" is a specious argument.  There is no need to
transform the data before validation.

When you do this you shift from thinking about the original data to thinking
about Python classes, which may or may not be an accurate representation.
And you think about transforming data instead of using data.


### Represent our own data in json too.

- Then we store it in simple text file.
- super easy I/O with Python
- cross-platform.  Totally transferable to other language.  Try that with classes.
   

### Unstated Assumptions

Needless transformation

Unstated assumptions in code should never go unquestioned.


- https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html
- https://docs.biothings.io/en/latest/
- https://stackoverflow.com/questions/2067472/what-is-jsonp-and-why-was-it-created
  jsonp == cross-domain requests
  but CORS is better.
- https://docs.mychem.info/en/latest/doc/chem_annotation_service.html
  a super simple API.  No swagger.
  uses optional jsonp, which is antiquated.

- https://github.com/bio-tools/OpenAPI-Importer     competition ??????
- https://www.biorxiv.org/content/10.1101/170274v1.full.pdf
    has list of biology openAPI services
- https://github.com/BiGCAT-UM/EnsemblOpenAPI
- http://www.ebi.ac.uk/proteins/api/swagger.json     NO
- https://www.ebi.ac.uk/proteins/api/openapi.json    yes

https://raw.githubusercontent.com/BiGCAT-UM/EnsemblOpenAPI/master/swagger.json

- https://libretranslate.com/docs/
- https://swagger.io/tools/swagger-codegen/  competition.........
- https://github.com/swagger-api/swagger-codegen  the actual code
  still compatible w/ Python 2.




- https://stackoverflow.com/questions/61112684/how-to-subclass-a-dictionary-so-it-supports-generic-type-hints
  Interesting discussion of subclassing builtins.


Denver Open Data.   I wonder.
- https://dataportals.org/portal/denver
- https://opendata-geospatialdenver.hub.arcgis.com
Crap.  Totally non-automatible.

- https://opentelemetry.io/docs/languages/

Walker...
- https://www.datascienceassn.org/resources

Walker's data science laws...
http://www.datascienceassn.org/sites/default/files/Walker%27s%20Data%20Science%20Laws%20by%20Michael%20Walker%20-%20Slides.pdf


https://cmd2.readthedocs.io/en/0.9.9/alternatives.html


#### bad things about DAO

Typical scenario...  
- DAO is written
- It is the interpretation of a programmer.  Not a person famiilar with the
  domain.
- It does not change for about 2 years.  
- because it is working code.
- Then it gets thrown out.

Result:  The beginner interpretation is set in stone, bugs and all.
  Until 2 years later, when it gets thrown out in favor of a new interpretation., 
  also in the DAO tradition.

When the business users ask us to solve a given problem, we can do one of two
things (or more).
1.   solve the exact problem.
2.   solve the exact problem while providing more general tools to solve
     problems LIKE this one.

Caveman Programming.
DAOs OK for things that are not business logic, critical to the customer.
OK for Infra?  I think not.  Look at infra code.  It is always (?) written in way
that best solves the problem (haha!) even when it means having to learn tricky,
picky systems;  github actions, Jenkins, ansible, etc.
If we hand the client something to solve their deep problems and it is the
interpretation of a beginner, we hamper their ability to solve business critical
problems.

The actual code is clearly an afterthought.


#### A perfectly worthless DAO

The class below encapsulates a set of parameters to a POST endpoint of some API.
The endpoint requires several parameters, with specific types; str, list, etc.
Can you see any problem with it?

```
   class Foo(PydanticBase):
       param: dict
```

The information content of the class is exactly equivalent to saying, "It is
a POST request.".
When the code failed, the debugging programmer would have liked to get useful
information from the class.  Unfortunately there is no useful information there.
The programmer had to go and look 
elsewhere
--at the swagger file-- 
to get the correct parameters.
(there was no swagger in this case.  Or swagger wss generated from code,
yielding worthless swagger.

This sort of thing happens a lot.

In reality, worthless would be an improvement.  This class subtracts value.


#### Worse than worthless

That complex way of doing nothing.

```
    def lazy_load(something):
        def inner(blah):
           return Flask.thing()  # something like this
        return inner
```


#### why?

The landscape is crowded with Python validation libraries.  Why would I create
another one?  Because...

1.  It's obviously not a definitively solved problem
B.  I have a different way of doing it.

A big part of the new vision is eliminating needless transformation.  So things
like DAOs have no place in it.  Yes, I'm saying a DAO is a needless
transformation.  Maybe not always, but I've yet to see a needful one.  If you
think about it, you will notice that the only benefit of the average DAO is the
dot notation for attribute access.  You don't need DAO for that.  If we need it
we will do it, without resorting to the LCD that is DAO.

- LCD:  lowest common denominator

btw.  It's not so much a data validation library as a set of techniques for
accessing APIs.  Validation is part of it, but by no means the primary focus.
Important, yes, but not the center of the universe.


