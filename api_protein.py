import json
from collections import defaultdict

import httpx
import jsonref
from jsonschema import ( Draft7Validator, FormatChecker,)

from tools import (
    raw_swagger, 
    local,        # not a tool.  It is data.
    common,        # not a tool.  It is data.
    retry_call,
    extract_from_dict_list,
)


def parameters_to_schema(parameters):
    pr = parameter_required(parameters)
    return {
        'required': [key for key in pr if pr[key]],
        'properties': parameter_schemas(parameters), 
        'additionalProperties': False, 
        'type': 'object', 
        }


def parameter_locations(parameters):
    return extract_from_dict_list(parameters, 'in')

def parameter_schemas(parameters):
    return extract_from_dict_list(parameters, 'schema')

def parameter_required(parameters):
    return extract_from_dict_list(parameters, 'required')


def protein_validator(endpoint, verb='get'):
    """Return a validator for `(endpoint, verb)`.
    """
    jdoc = jsonref.loads(json.dumps(altered_raw_swagger(local.swagger.protein)))
    parameters = jdoc['paths'][endpoint][verb]['parameters']
    schema = parameters_to_schema(parameters)
    return Draft7Validator(schema, format_checker=FormatChecker())


@retry_call()
def call(endpoint, verb, params):
    """Call (endpoint, verb) with params.
    """
    (url, verb, request_params) = prepped(endpoint, verb, params)
    request = httpx.Request(verb, url, **request_params)
    with httpx.Client(base_url=local.api_base.protein) as client:
        return client.send(request)  


def prepped(endpoint, verb, args):
    """Prepare args for passing to (endpoint, verb).
    """
    rs = altered_raw_swagger(local.swagger.protein)
    paths = jsonref.loads(json.dumps(rs))['paths']
    location = parameter_locations(paths[endpoint][verb]['parameters'])
    request_params = {}
    query = {}
    for arg in args:
        plocation = location[arg] if arg in location else 'query'
        if plocation == 'path':
            endpoint = endpoint.replace('{'+arg+'}', str(args[arg]))
        elif plocation == 'query':
            query[arg] = args[arg]
    if query:
        request_params['params'] = query
    return (local.api_base.protein + endpoint, verb, request_params)


def altered_raw_swagger(swagger_path):
    """Alter raw data to conform with local code assumptions.
    """
    jdoc = raw_swagger(swagger_path)
    patch = dict(parameters=[])
    jdoc['paths']['/das/s4entry']['get'].update(patch)
    jdoc['paths']['/']['get'].update(patch)
    return jdoc


# test test test test test test test test test test test test test test test
##############################################################################
from test_data_protein import test_parameters
from pprint import pprint


# TODO: clarify messaging.
def protein_validate_and_call():
  try:
    bad_param_but_ok = defaultdict(list)
    good_param_not_ok = defaultdict(list)
    paths = altered_raw_swagger(local.swagger.protein)['paths']       # protein
    for endpoint in paths:
        for verb in paths[endpoint]:
            assert verb in 'get post'
            validator = protein_validator(endpoint, verb)
            print(endpoint, verb)
            if endpoint in test_parameters:
                things = test_parameters[endpoint]
                for params in things['good']:
                    assert validator.is_valid(params)
                    print('   ok good valid', params)
                    response = call(endpoint, verb, params)
                    if not response.is_success:
                        good_param_not_ok[(endpoint, verb)].append(params)
                    if response.is_success:
                        print('   ok good call')
                for params in things['bad']:
                    assert not validator.is_valid(params)
                    print('   ok bad NOT valid', params)
                    response = call(endpoint, verb, params)
                    if response.is_success:
                        bad_param_but_ok[(endpoint, verb)].append(params)
    bad_param_but_ok = dict(bad_param_but_ok)
    good_param_not_ok = dict(good_param_not_ok)
    # TODO: local validation.  eg, prevent {}, etc.
    # TODO: start here.........
    # with local validation.
    """
    >>> pprint(good_param_not_ok)
    {('/epitope', 'get'): [{}, {'accession': 'xxxxxxxx'}],
     ('/proteins', 'get'): [{}, {'accession': 'xxxxxxxx'}],
     ('/uniparc/sequence', 'post'): [{'rfActive': 'true'},
                                 {'rfActive': 'false'},
                                 {'rfDbid': 'AAC02967,XP_006524055'},
                                 {'rfDdtype': 'EMBL,RefSeq,Ensembl'}]}
    """

  finally:
    globals().update(locals())


def test_altered_raw_swagger():
    jdoc = altered_raw_swagger(local.swagger.protein)
    assert jdoc['paths']['/das/s4entry']['get']['parameters'] == []
    assert jdoc['paths']['/']['get']['parameters'] == []


# aside #
##############################################################################


rs = raw_swagger(local.swagger.protein)
paths = jsonref.loads(json.dumps(rs))['paths']
assert len(paths) == 57

def get_component_schemas_protein():    # EBI
    rs = raw_swagger(local.swagger.protein)
    with_refs = jsonref.loads(json.dumps(rs))
    components = with_refs['components']
    return components['schemas']


ps = get_component_schemas_protein()
assert len(ps.keys()) == 96
pt = ps['ProteinType']
st = ps['SequenceType']
s = ps['Sequence']
# Nice schemas.  Each entry in every schema has 'xml': {'attribute': True},
# which could be eliminated w/o effect.

#https://www.ncbi.nlm.nih.gov/genbank/samplerecord/
#                    Examples: A2BC19, P12345, A0A023GPI8

# sample_query_params = {
#     'accession': test_parameters['/proteins']['good'][0]['accession'],
# }
head = {'accept': 'application/json'}  # some endpoints default to XML.
head = common.headers.accept.json

# https://www.ebi.ac.uk/proteins/api/doc/#!/taxonomy/getTaxonomyLineageById
# shows /taxonomy endpoints but these are not present in the OpenAPI file.


def parameter_descriptions(parameters):
    return extract_from_dict_list(parameters, 'description')


def extracto(parameters):
    def inner(key):
        return extract_from_dict_list(parameters, key)
    return inner


try:
    fetch = extracto(parameters)
    locations = fetch('in')
    descriptions = fetch('description')
    schemi = fetch('schema')
    reqs = fetch('required')
    req2 = parameter_required(parameters)
    assert reqs == req2
    p2s = parameters_to_schema(parameters)
except NameError:
    pass

# some keys found in endpoints
# 'tags summary description operationId responses'.split():

    """
    NOTE: `description` of parameters are excellent!
    """


def demo_patch():
    # AHA!    brainwave!!! not quite correct.
    # Must update the leaf.
    jdoc = jsonref.loads(json.dumps(rs))
    das_path = jdoc['paths']['/das/s4entry'] 
    das_get = jdoc['paths']['/das/s4entry']['get']
    patch = dict(paths={'/das/s4entry': dict(get=dict(parameters=[]))})
    jdoc.update(patch)
    assert jdoc['paths']['/das/s4entry']['get']['parameters'] == []
    globals().update(locals())

# pv = protein_validator('/uniparc/sequence', 'post')
# schema = {
#  'properties': {
#     'rfActive': {'pattern': 'true|false', 'type': 'string'},
#     'rfDbid': {'type': 'string'},
#     'rfDdtype': {'type': 'string'},
#     'rfTaxId': {'pattern': '^[0-9]+(,[0-9]+)*$', 'type': 'string'}},
#  'required': [],
#  'additionalProperties': 'false', 
#  'type': 'object', 
#  }
# vd = Draft7Validator(schema, format_checker=FormatChecker())
# params = {'rfActive': 'true'}
# vd.validate(params)
# params = {'rfActive': 'xxxxxxxx'}
# vd.validate(params)
# params = {'x': 'xxxxxxxx'}
# vd.validate(params)

# schema = {
#   "type": "object",
#   "properties": {
#     "number": { "type": "number" },
#     "street_name": { "type": "string" },
#     "street_type": { "enum": ["Street", "Avenue", "Boulevard"] }
#   }
# }
# vd = Draft7Validator(schema, format_checker=FormatChecker())
# instance = { "number": 1600, "street_name": "Pennsylvania", "street_type": "Avenue" }
# vd.validate(instance)
# instance = { "number": '1600', "street_name": "Pennsylvania", "street_type": "Avenue" }
# vd.validate(instance)

#     parameters = paths[endpoint][verb]['parameters']
#     schema = parameters_to_schema(parameters)
#     f = lambda ob: Draft7Validator(schema, format_checker=FormatChecker()).is_valid(ob)


