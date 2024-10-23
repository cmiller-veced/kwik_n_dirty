"""
Identifier class(es)

OSDU had an identifier, we will call it, XID.
It was originally described in a Word document, something like this.
XID is a string with 3 sections delimited by ':'.
The three sections specify information relevant to head, body and tail.
Contents of each section is a string.

This is then coded into each project in whatever programming languge(s) is/are
used.  In Python the definition always went something like...

Pydantic (or the validation lib de jour) is used for validation.

class Xid(pydantic.something):
    # TODO: put regex here.
    # TODO: put regex here.
    # TODO: put regex here.

    head: str
    body: str
    tail: str

    to_dict(self):
        ...
    @classmethod
    from_dict(self):
        ...
    to_string(self):
        ...
    @classmethod
    from_string(self):
        ...

Each Python project copy-pasted this definition
Each Python project copy-pasted this definition, with 2-3 different versions in
total, of the regexes.   This difference is not good.  Xid is used throughout
the company.  Seems to me a single definition in a single location would be
ideal.  Defined outside any programming language but usable by any language
would be a plus.
JSONschema solves the problem.


btw.  Note that the Xid class above is a Python class.  The business users
defined it as a string.  Users think of it as a string with three distinct
parts.  So why do the programmers begin by defining it as something different?
This immediately moves us away from dealing with the business problem.

So we define it as a string.  It's a special sort of string so we ensure it
conforms to expectations.  This can be done with either a function or a method.
For now we use a function.  Because, again, the business problem says we want to
verify correctness, but is indifferent to method vs function.

"""


from functools import singledispatch
import jsonschema
from jsonschema import Draft7Validator
import pytest


# Data
# ##########################################################################

xid_names = 'head body tail'.split()
alphanumeric3 = '[0-9A-Za-z]{3}'

xid_schema = dict(
    type='string',
    pattern= f"^{alphanumeric3}:{alphanumeric3}:{alphanumeric3}$"
)

did_schema = dict(
    additionalProperties = False,
    required = xid_names,
    type='object',
    properties = dict(
        head= dict( type='string', pattern= f"^{alphanumeric3}$"),
        body= dict( type='string', pattern= f"^{alphanumeric3}$"),
        tail= dict( type='string', pattern= f"^{alphanumeric3}$"),
    )
)


# automated conversions
# ###########################################################################
#
# Sometimes conversion is a business problem.
# But in general not conversion from/to instance.
# but instead, conversion between builtin types.
# eg Xid <-> dict


# specific to xid
# A dict subclass with auto-conversion to str.
class cdict(dict):
    def __str__(self):
        return ':'.join([self[key] for key in xid_names])


# specific to xid
# A str subclass with auto-conversion to dict.
class cstr(str):
    def __iter__(self):
        for (name, thing) in zip(xid_names, self.split(':')):
            yield (name, thing)


# general
# validated dict subclasses
def validated_for_dict(typ, schema):
    class Inner(typ):
        def __init__(self, *args, **kwargs):
            Draft7Validator(schema).validate(dict(*args, **kwargs))
            super().__init__()
            self.update(*args, **kwargs)
    return Inner
def validated_for_dict(schema):
    class Inner(dict):
        def __init__(self, *args, **kwargs):
            Draft7Validator(schema).validate(dict(*args, **kwargs))
            super().__init__()
            self.update(*args, **kwargs)
    return Inner



# general
# validated str subclasses
def validated_for_str(typ, schema):
    class Inner(typ):
        def __init__(self, thing):
            Draft7Validator(schema).validate(thing)
            super().__init__()
    return Inner


# general
# TODO: use singledispatch instead.
def validated(typ, schema):
    if issubclass(typ, dict):
        return validated_for_dict(typ, schema)
    return validated_for_str(typ, schema)

# TODO: demonstrate the general behavior with different schemas.

# ############################################################################


# TODO: make tests easier to follow.
def demo_subclasses():
    """
    super-snappy auto-validation for subclasses of builtin types.
    # demo the two validating, but not auto-converting, classes.
    """
    d = {'head': 'foo', 'body': 'bar', 'tail': 'bat'}
    v2 = validated(dict, did_schema)
    assert d == v2(d)  # OK

    cv2 = validated(cdict, did_schema)
    assert d == cv2(d)  # OK

    s = 'foo:bar:xxx'
    vsn = validated(str, xid_schema) 
    assert vsn(s) == s

    vsn = validated(cstr, xid_schema) 
    assert vsn(s) == s

    smap = {str: xid_schema, dict: did_schema, }
    for ty in test_data:
        T = validated(ty, smap[ty])
        print(ty)
        print('  good...')
        for good in test_data[ty]['good_ones']:
            thing = T(good)
            assert thing == good
            assert isinstance(thing, ty)     
            assert type(thing) is not ty
            print('   ', good)
        print('  bad...')
        for bad in test_data[ty]['bad_ones']:
            with pytest.raises(jsonschema.exceptions.ValidationError):
                T(bad)
            with pytest.raises(jsonschema.exceptions.ValidationError):
                T(bad)
            print('   ', bad)

    # super-snappy conversions between subclasses of builtin types.
    xid = validated(str, xid_schema)
    xid = validated(cstr, xid_schema)
    s0 = 'foo:bar:bat'
    d0 = {'head': 'foo', 'body': 'bar', 'tail': 'bat'}
    s = xid(s0)
    assert isinstance(s, str)     
    assert type(s) is not str
    assert type(s) is xid
    for pair in s:
        assert type(pair) is tuple
        assert len(pair) == 2
    d = dict(s)
    assert d == d0

    dxid = validated(cdict, did_schema)
    d2 = dxid(d0)
    assert d2 == d0
    s2 = str(d2)
    assert s2 == s0

    # New, converting subclasses w/o validation.
    cd = cdict(d0)
    assert type(cd) is cdict
    assert cd == d0
    assert str(cd) == s0

    cs = cstr(s0)
    assert type(cs) is cstr
    assert cs == s0
    assert dict(cs) == d0

    globals().update(locals())


test_data = {
    str: dict(
        good_ones=['foo:bar:bat', 'foo:222:BAT'],
        bad_ones=['', 'x', 'foot:bar:bat'],
        ),
    dict: dict(
        good_ones=[dict(head='xxx', body='aB2', tail='ttt')],
        bad_ones=[{}],
        ),
}


import dataclasses
from dataclasses import dataclass, make_dataclass, field

# auto-generate dataclasses.
Cid = make_dataclass('xid', [(name, str) for name in xid_names])
c = Cid('h', 'b', 't')

Cid = make_dataclass('xid', xid_names, frozen=True)
c = Cid('h1', 'b1', 't1')
assert c.head == 'h1'
assert c.body == 'b1'
assert c.tail == 't1'
with pytest.raises(dataclasses.FrozenInstanceError):
    c.head = 'xxxx'

# TODO: class factory                              DONE
# TODO: separate class factory for dict vs str.    DONE
# TODO: find out about dataclasses.                wip
# TODO: find out about TypedDict.                  like a dataclass
# TODO: review NamedTuple.                         wip
# TODO: auto conversions.                          DONE
# https://github.com/python-attrs/attrs

