

#def identity_func(x): return x


def altered_dict_list(list_of_dict, func):
    return [func(d) for d in copy.deepcopy(list_of_dict)]



def preprocess_schemas(schemas):
    """
    Preprocessing can have multiple steps because of multiple problem sources.
    - type errors by the swagger author.  eg swagger says int but should be str.
    - things we just want to change in the schema, eg additionalProperties.
    - shortcomings of jsonschema,  eg date formats?
    s3['additionalProperties'] = False   # TODO: move to preprocessing step.
    """
    return schemas


def endpoint_names(swagger_doc):
    return list(swagger_doc['paths'].keys())







# Validation using jsonschema #
# ######################################################################## #

def validate_jsonschema_with_refs():
    good_ones = [
        {"name": 'kittyX', 'photoUrls': []},
        {"name": 'kittyX', 'photoUrls': [], 'category': {}},
        {"name": 'kittyX', 'photoUrls': [], 'status': 'sold'},
        {"name": 'kittyX', 'photoUrls': [], 'category': {}, 'status': 'sold'},
    ]
    bad_ones = [
        {},
        {"name": 'kittyX'},
        {"name": 'kittyX', 'photoUrls': [], 'category': ''}, 
        {"name": 'kittyX', 'photoUrls': [], 'status': ''},
    ]
    rs = raw_swagger(pet_swagger_local)
    with_refs = jsonref.loads(json.dumps(rs))
    good_schema = with_refs['definitions']['Pet']  # The behavior we want
    bad_schemas = [{}, dict(foo=2)]   # jsonschema allows any dict to be a schema.

    vd = lambda ob: validate(instance=ob, schema=good_schema)
    for ob in good_ones:
        validate(instance=ob, schema=good_schema)
        print('ok good', ob)

    for ob in bad_ones:
        try:
            validate(instance=ob, schema=good_schema)
        except jsonschema.exceptions.ValidationError:
            print('ok bad', ob)

    for schema in bad_schemas:
        validate(instance={}, schema=schema)
        print('crap!')

    globals().update(locals())





# Recursion over a heterogeneous data structure.
@singledispatch
def recur(arg, fun=identity_func):
    return fun(arg)

@recur.register
def _(arg: list, fun=identity_func):
    return [recur(fun(thing)) for thing in arg]

@recur.register
def _(arg: dict, fun=identity_func):
    #    fun(arg)    fails disastrously
    return {key:recur(fun(arg[key])) for key in arg}
    # TODO: fooeey!
    # This fails for the problem of deleting dict keys.
    # but...

@singledispatch
def delete_key(arg, key):
    return arg

@delete_key.register
def _(arg: dict, key):
    try:
        arg.pop(key)   # NOTE  mutates input
    except KeyError:
        pass
    return {k: delete_key(arg[k], key) for k in arg}

@delete_key.register
def _(arg: list, key):
    return [delete_key(thing, key) for thing in arg]

def test_delete_key():
    test_d = dict(foo=2, xml=3)
    dt = delete_key(test_d, 'xml')
    assert dt == test_d
    assert dt is not test_d




@singledispatch
def recur1(arg, indent=0):
    print(f'{" "*indent}{arg}')

@recur1.register
def _(arg: list, indent=0):
    for thing in arg:
        recur1(thing, indent=indent+1)

@recur1.register
def _(arg: dict, indent=0):
    for key in arg:
        recur1(key, indent=indent+1)
        recur1(arg[key], indent=indent+1)
        print()
# TODO: This is good but extremely limited.
# It does the recursion correctly but simply prints out stuff in a totally rigid
# way.





# fetch from deeply nested dicts.
# TODO: add ability to do similar with lists in the mix.
@singledispatch
def deep_key(keys, dct):
    keys.reverse()
    while keys:
        key = keys.pop()
        dct = dct[key]
    return dct

@deep_key.register
def _(keys: str, dct):
    return deep_key(keys.split(), dct)

def test_deep_key():
    rs = raw_swagger(pet_swagger_local)
    assert deep_key('definitions Category', rs) == rs['definitions']['Category']
    assert deep_key(['definitions', 'Category'], rs) == rs['definitions']['Category']



def test_recursion():
  try:
    rs = raw_swagger(pet_swagger_local)
    print(len(str(rs)))
    print(len(rs))
    rs_keys = ['swagger', 'info', 'host', 'basePath', 'tags', 'schemes', 'paths', 'securityDefinitions', 'definitions', 'externalDocs']
    assert sorted(list(rs.keys())) == sorted(rs_keys)
    for key in rs_keys:
        print(key, type(rs[key]))
        print(rs[key])
        print()
    recur1(rs)

  finally:
    globals().update(locals())


def test_all():
    test_deep_key()
    test_recursion()
    validate_jsonschema_with_refs()


#test_all()
# TODO: test the recursion by finding all dict items with key == '4xx'
#   esp 415
# TODO: find some complexity metrics
# LOC and McCabe are both good.
# I'd like a version of McCabe that accounts for 3rd party libs.
# or something like that.


# https://lwn.net/Articles/818971/    Good read.
def get(obj, path):
    for step in path.split("-"):
        obj = obj[step]
    return obj
#print(get(catalog, 'clothing-mens-shoes-extra_wide-quantity'))


def namespacify(thing):
    ugly_hack = json.dumps(thing, indent=1)
#    ugly_hack = json.dumps(thing)   # when ugly_hack is no longer needed we
#    will use this line instead.
    return json.loads(ugly_hack, object_hook=lambda d: SimpleNamespace(**d))
    # ugly_hack:    indent=1
    # ugly_hack is required, and works because ...
    # By the way, this specific problem (with json.dumps) can be bypassed by passing any of the "special" parameters dumps accepts (e.g indent, ensure_ascii, ...) because they prevent dumps from using the JSON encoder implemented in C (which doesn't support dict subclasses such as rpyc.core.netref.builtins.dict). Instead it falls back to the JSONEncoder class in Python, which handles dict subclasses.
    # https://github.com/tomerfiliba-org/rpyc/issues/393


def test_namespace():    # dict => namespace
  try:
    rs = raw_swagger(pet_swagger_local)
    ns0 = namespacify(rs)

    with_refs = jsonref.loads(json.dumps(rs))
    ns = namespacify(with_refs)     # ugly_hack required for this 

    assert ns0.definitions.Pet.properties.category == namespacify(rs['definitions']['Pet']['properties']['category'])

    assert ns.definitions.Pet.properties.category == namespacify(with_refs['definitions']['Pet']['properties']['category'])
    assert ns.definitions.Pet.properties.category == namespacify(deep_key('definitions Pet properties category', with_refs))

    # convert namespace back to dict.
    v0 = vars(ns)  # ok but not recursive

    # recursively convert namespace back to dict.
    v = json.loads(json.dumps(ns, default=lambda s: vars(s)))

  finally:
    globals().update(locals())








1 and print('x'*33)    # interesting trick
0 and print('y'*33)    # interesting trick
0 or print('z'*33)    # interesting trick


wtf_namespace = """
>>> pram.in
  File "<stdin>", line 1
    pram.in
         ^
SyntaxError: invalid syntax
"""      # what's the problem?




####################### Insert query params ########################


def fetch_endpoint_parameter_names(endpoint):
    return [s.split('}')[0] for s in endpoint.split('{') if '}' in s]


# endpoint_QUERY_params
def insert_endpoint_params(endpoint, parameters):
    if not '{' in endpoint:
        return endpoint
    env = Environment(autoescape=select_autoescape())
    template = env.from_string(templatified(endpoint))
    return template.render(**parameters)


def test_insertion():
    sample_query_params = {
            'typeId': 'TTTTTT',
            'stationId': 'sid',
            'locationId': 'LLLLLL',
        }
    ep = '/products/types/{typeId}/{stationId}/{locationId}'
    pns = fetch_endpoint_parameter_names(ep)
    assert pns == ['typeId', 'stationId', 'locationId']
    new_ep = insert_endpoint_params(ep, sample_query_params)
    assert new_ep == '/products/types/TTTTTT/sid/LLLLLL'
 

####################### ^ Insert query params ^ ########################




# general
def templatified(s):
    return s.replace('{', '{{').replace('}', '}}')


# TODO: pagination



# Jmespath (stronger than jsonpath)
# ###########################################################################

import jmespath


# TODO: function to update json doc based on jmespath.
def demo_jmespath():
    q = 'store.book[0]'           # first book
    q = ''
    q = 'store.book[*].price'     # all book prices
    q = 'store.*.price'           # 399
    q = '*.price'           # []
    q = '**.price'           # exception
    q = '*.*.price'           # [[399]]
    q = '[].*.price'           # None
    q = '..price'                 # fails to get all prices.
 
    jdoc = {
      "store": {
        "book": [
          { "author": "Nigel Rees",
            "title": "Sayings of the Century",
            "price": 8.95
          },
          { "author": "J. R. R. Tolkien",
            "title": "The Lord of the Rings",
            "isbn": "0-395-19395-8",
            "price": 22.99
          }
        ],
        "bicycle": {
          "color": "red",
          "price": 399
        }
      }
    }

    path = jmespath.search('foo.bar', {'foo': {'bar': 'baz'}})
    j = jmespath.search('foo.bar', jdoc)
    q = '..price'                 # exception
    q = 'store.*.price'           # [399]
    q = 'store.*.*.price'           # [[]]
    q = 'store.book.*.price'           # None
    q = 'store.book.[*].price'           # None
    q = 'store.book[*].price'           # [8.95, 22.99]
    q = 'store.book[*]'           # the two books
    q = 'store.*'           # a two-element list.  First element is another list
    # containing the two books.  Second element is the bike.

    # https://pypi.org/project/jmespath/
    expression = jmespath.compile(q)
    j = expression.search(jdoc)
    j2 = [[{'author': 'Nigel Rees', 'title': 'Sayings of the Century', 'price': 8.95}, {'author': 'J. R. R. Tolkien', 'title': 'The Lord of the Rings', 'isbn': '0-395-19395-8', 'price': 22.99}], {'color': 'red', 'price': 399}]
    globals().update(locals())

# Find out if jmespath set values too, rather than only extract.
# Methinks it is only for extracting.
# Write something to take jmespath.
#
#


# Principle:  Use cross-platform tools.  
# jmespath
# jsonschema
# bash   (shows up in GHA, terraform, ansible, etc)





# flatten list

j3 = [['a', 'b'], ['c']]
jj = [x for thing in j3 for x in thing]
for thing in j3:
    for x in thing:
        x

j3 = [['a', 'b'], 'c']
# goal == 'abc'
[thing for thing in j3 ]
for thing in j3:
    for x in thing:
        x
jt = [x for thing in j3 for x in thing]
assert jt == ['a', 'b', 'c']
# ok but works only because 'c' is a single letter
j3 = [['aa', 'b'], 'cc']
jt = [x for thing in j3 for x in thing]
assert jt == ['aa', 'b', 'c', 'c']
jt = [x if type(thing) is list else thing for thing in j3 for x in thing]
# not quite right
assert jt == ['aa', 'b', 'cc', 'cc']
#jt = [x for thing in j3 if type(thing) is list else [thing] for x in thing]
#jt = [thing for thing in j3 if type(thing) is list else [thing]]  # invalid syntax
#jt = [thing else 'x' for thing in j3 if type(thing) is list]  # invalid syntax

jt = [a if a else 2 for a in [0,1,0,3]]
jt = [a if a else [2] for a in [0,1,0,3]]
#jt = [thing for thing in j3 if (type(thing) is list) else [thing]]  # invalid syntax

jtt = [thing if (type(thing) is list) else [thing] for thing in j3]  # ok
# but not solving the problem.
assert jtt == [['aa', 'b'], ['cc']]
# which can then be used with the OTHER list comprehension.  But sort of makes
# the problem more complex, and only addresses one level of nesting
# tldr; 
# much complicated in a list comprehension.
# Try a recursive function.





# on stackoverflow we find this...
def flatten(container):
    for i in container:
        if isinstance(i, (list,tuple)):
            for j in flatten(i):
                yield j
        else:
            yield i
nests = [1, 2, [3, 4, [5],['hi']], [6, [[[7, 'hello']]]]]
assert list(flatten(nests)) == [1, 2, 3, 4, 5, 'hi', 6, 7, 'hello']
# snappy

class DotDict(dict):
    """
    >>> d = DotDict(foo=2)
    >>> assert d['foo'] == d.foo
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


