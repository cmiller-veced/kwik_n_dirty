import json

import httpx
import jsonref
from jsonschema import FormatChecker

from info import local
from tools import (raw_swagger, retry_call, extract_from_dict_list,
    dvalidator, LocalValidationError,)

from other import (prep_func, parameters_to_schema, dv, dcall,)

class ValidDataBadResponse(LocalValidationError): pass

class NonTruthy(LocalValidationError): pass

class InvalidAccessionId(LocalValidationError): pass


def local_validate(params):
    """Catch data problems missed by the schema.
    """
    if not params:
        raise NonTruthy(params)
    if params == {'accession': 'xxxxxxxx'}:
        raise InvalidAccessionId(params)


#def altered_raw_swagger(swagger_path):
def altered_raw_swagger(jdoc):
    """Alter raw data to conform with local code assumptions.
    """
    patch = dict(parameters=[])
    jdoc['paths']['/das/s4entry']['get'].update(patch)
    jdoc['paths']['/']['get'].update(patch)
    return jdoc


def head_func(endpoint, verb):
    return {}


# TODO: further streamlining.
protein_validator = dv(local.swagger.protein, local_validate, altered_raw_swagger)
call = dcall(local.api_base.protein, local.swagger.protein, head_func, altered_raw_swagger)


# test test test test test test test test test test test test test test test
##############################################################################
from test_data_protein import test_parameters
from pprint import pprint
from collections import defaultdict


# TODO: clarify messaging.
def protein_validate_and_call():
  try:
    bad_param_but_ok = defaultdict(list)
    good_param_not_ok = defaultdict(list)
    rs = raw_swagger(local.swagger.protein)
    paths = altered_raw_swagger(rs)['paths']
#    paths = altered_raw_swagger(local.swagger.protein)['paths']       # protein
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
                        raise ValidDataBadResponse(params)
                        """
                        {'rfActive': 'true'}   Returns a bad response.
                        {'rfActive': True}   Fails validation.
                        {'rfActive': True}   Returns a good response?
                        BUT This fucked.
                        The httpx (or some other Python lib) insists on using
                        True instead of 'true'.
                        But what the api actually wants is 'true', the json
                        version of True.
                        NO NO NO NO NO NO NO NO NO NO NO NO NO NO NO NO NO NO 
                        NO NO NO NO NO NO NO NO NO NO NO NO NO NO NO NO NO NO 
                        NO NO NO NO NO NO NO NO NO NO NO NO NO NO NO NO NO NO 
                        The above returns a 500 response.
                        I have no idea if it is because of 'true' vs True.
                        But I think NOT.
                        Look at the test data.  It shows the response.
                        """
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

