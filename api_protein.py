import json

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

class BadInput(Exception): pass

def parameters_to_schema(parameters):
    return {
        'required': list(parameter_required(parameters)),  # TODO: this grabs False values.  FIX IT
        'parameters': parameter_schemas(parameters), 
        }


def parameter_locations(parameters):
    return extract_from_dict_list(parameters, 'in')

def parameter_schemas(parameters):
    return extract_from_dict_list(parameters, 'schema')

def parameter_required(parameters):
    return extract_from_dict_list(parameters, 'required')


def protein_validator(endpoint, verb='get'):
    """Return a function to validata parameters for `(endpoint, verb)`.
    """
    rs = raw_swagger(local.swagger.protein)
    paths = jsonref.loads(json.dumps(rs))['paths']
    parameters = paths[endpoint][verb]['parameters']
    print(endpoint, verb, len(parameters))
    schema = parameters_to_schema(parameters)
    return lambda ob: Draft7Validator(schema, format_checker=FormatChecker()).is_valid(ob)


@retry_call()
def call(endpoint, verb, params):
    """Call the endpoint+verb with request_params.
    """
    (url, verb, request_params) = prepped(endpoint, verb, params)
    request = httpx.Request(verb, url, **request_params)
    with httpx.Client(base_url=local.api_base.protein) as client:
        return client.send(request)  


def prepped(endpoint, verb, args):
    """
    # TODO: docstring
    parameters:  defined in swagger.
    args:  a specific instance.
    """
    if type(args) is not dict:
        print('..................... BadInput ........................ ', args)
        raise BadInput()
        # TODO: this is a problem with my test data.   FIX
    rs = raw_swagger(local.swagger.protein)
    paths = jsonref.loads(json.dumps(rs))['paths']
    things = paths[endpoint][verb]['parameters']
    location = parameter_locations(things)
    request_params = {}
    query = {}
    for arg in args:
        plocation = location[arg] if arg in location else 'query'
        print('populate_request', arg, plocation, args[arg])
        if plocation == 'path':
            endpoint = endpoint.replace('{'+arg+'}', str(args[arg]))
        elif plocation == 'query':
            query[arg] = args[arg]
    if query:
        request_params['params'] = query
    return (local.api_base.protein + endpoint, verb, request_params)


# test test test test test test test test test test test test test test test
##############################################################################
from test_data_protein import test_parameters
from pprint import pprint

oddballs = set()   # TODO: remove
# TODO:  but first, deal with the oddball in a constructive way.
#    assert oddballs == {('/uniparc/sequence', 'post')}
ignore_endpoints = ['/']
ignore_endpoints = ['/', '/das/s4entry']   # but revisit this one.


def protein_validate_and_call():
  try:
    paths = raw_swagger(local.swagger.protein)['paths']       # protein
    for endpoint in ignore_endpoints:
        paths.pop(endpoint)
    for endpoint in paths:
        for verb in paths[endpoint]:
            assert verb in 'get post'
#                print(endpoint, verb)
            if verb != 'get':
                oddballs.add((endpoint, verb))
            is_valid = protein_validator(endpoint, verb)
            if endpoint in test_parameters:
                things = test_parameters[endpoint]
                for params in things['good']:
                    assert is_valid(params)
                    print('   ok good valid', params)
                    response = call(endpoint, verb, params)
                    if response.is_success:
                        print('   ok good call')
                for params in things['bad']:
                    #assert not is_valid(params)
                    print('   ok bad NOT valid ??????????', params)
                    try:
                        response = call(endpoint, verb, params)
                    except BadInput:
                        continue
                    assert not response.is_success
  finally:
    pass


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

sample_query_params = {
    'accession': test_parameters['/proteins']['good'][0]['accession'],
}
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
