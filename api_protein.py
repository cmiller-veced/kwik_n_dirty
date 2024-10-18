import json
from collections import defaultdict

import httpx
import jsonref
from jsonschema import FormatChecker

from tools import (
    raw_swagger, 
    local,        # not a tool.  It is data.
    common,        # not a tool.  It is data.
    retry_call,
    extract_from_dict_list,
    dvalidator,
    LocalValidationFailure,
)

class NonTruthy(LocalValidationFailure): pass

class InvalidAccessionId(LocalValidationFailure): pass


def local_validate(params):
    """Catch data problems missed by the schema.
    """
    if not params:
        raise NonTruthy(params)
    if params == {'accession': 'xxxxxxxx'}:
        raise InvalidAccessionId(params)


def parameters_to_schema(parameters):
    pr = extract_from_dict_list(parameters, 'required')
    return {
        'required': [key for key in pr if pr[key]],
        'properties': extract_from_dict_list(parameters, 'schema'), 
        'additionalProperties': False, 
        'type': 'object', 
        }


def protein_validator(endpoint, verb='get'):
    """Return a validator for `(endpoint, verb)`.
    """
    jdoc = jsonref.loads(json.dumps(altered_raw_swagger(local.swagger.protein)))
    parameters = jdoc['paths'][endpoint][verb]['parameters']
    schema = parameters_to_schema(parameters)
    return dvalidator(local_validate)(schema, format_checker=FormatChecker())


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
    location = extract_from_dict_list(paths[endpoint][verb]['parameters'], 'in')
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
                        raise LocalValidationFailure(params)
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
  finally:
    globals().update(locals())


def test_altered_raw_swagger():
    jdoc = altered_raw_swagger(local.swagger.protein)
    assert jdoc['paths']['/das/s4entry']['get']['parameters'] == []
    assert jdoc['paths']['/']['get']['parameters'] == []


# aside #
##############################################################################

