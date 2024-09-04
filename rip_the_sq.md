# Ripping the Status Quo

x



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



### Do not try to guess what they/you will need

you will get it wrong.



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





### Unstated Assumptions

Needless transformation

Unstated assumptions in code should never go unquestioned.





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



# A worse-than-worthless class

Below goes in a Jupyter notebook?  NO.
It goes in a long document explaining / cataloging shortcomings of the DAO
approach.

'''
class CallSpecificEndpoint(PydanticModel):
    """
    The information content of this class is exactly equivalent to saying,
    'It's a POST call.'
    """
    parameters: dict

and then there was the Neptune database.
Gremlin queries translated to the above, one-trick.

'''

