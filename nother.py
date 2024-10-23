import json
import jsonref
from jsonschema import FormatChecker
import httpx

from tools import (dvalidator, raw_swagger, identity_func,
                   extract_from_dict_list,
                   retry_call,
                   LocalValidationError,
                   )

class ValidDataBadResponse(LocalValidationError): pass

class NonDictArgs(Exception): pass


def parameters_to_schema(parameters):
    pr = extract_from_dict_list(parameters, 'required')
    return {
        'required': [key for key in pr if pr[key]],
        'properties': extract_from_dict_list(parameters, 'schema'), 
        'additionalProperties': False, 
        'type': 'object', 
    }


def dv(config):
    swagger_path = config.swagger_path
    local_validate = config.validate
    altered_raw_swagger = config.alt_swagger
    def validator(endpoint, verb='get'):
        """Return a validator for `(endpoint, verb)`.
        """
        jdoc = jsonref.loads(json.dumps(raw_swagger(swagger_path)))
        jdoc = altered_raw_swagger(jdoc)
        parameters = jdoc['paths'][endpoint][verb]['parameters'] or {}
        globals().update(locals())
        schema = parameters_to_schema(parameters)
        return dvalidator(local_validate)(schema, format_checker=FormatChecker())
    return validator


# TODO: add headers to `prepped`       NO!!!!!!!!
def prep_func(api_base, 
              swagger_path, 
              altered_raw_swagger=identity_func,
              #              headers=None
    ):
#     """
#     headers is a function that accepts (endpoint, verb) and returns header(s) as
#     json/dict.
#     """
    def prepped(endpoint, verb, args):
      try:
        """Prepare args for passing to (endpoint, verb).
        """
        if not args:                                 # diff
            return (api_base + endpoint, verb, {})   # diff
        if type(args) is not dict:                   # diff
            raise NonDictArgs(args)

        jdoc = raw_swagger(swagger_path)
        jdoc = jsonref.loads(json.dumps(jdoc))
        rs = altered_raw_swagger(jdoc)   # TODO: must alter AFTER deref.
        paths = rs['paths']
        ev_params = paths[endpoint][verb]['parameters'] or {}
        location = extract_from_dict_list(ev_params, 'in')
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
#        heads = headers(endpoint, verb) if headers else None
#        return (api_base + endpoint, verb, request_params, heads)
        return (api_base + endpoint, verb, request_params)
      finally:
        globals().update(locals())
    return prepped

# TODO: add something to add headers to a few random endpoints to illustrate.
# Maybe.
# TODO: no need to test with bad params????????//
# Because those should be caught by validation...


def dcall(config):
    """
    """
    api_base = config.api_base
    swagger_path = config.swagger_path
    head_func = config.head_func
    altered_raw_swagger = config.alt_swagger

    prepped = prep_func(api_base, swagger_path, altered_raw_swagger)
    @retry_call()
    def call(endpoint, verb, params):
        """Call (endpoint, verb) with params.
        """
        if head_func:
            heads = head_func(endpoint, verb)
        else:
            heads = None
        (url, verb, request_params) = prepped(endpoint, verb, params)
        request = httpx.Request(verb, url, **request_params, headers=heads)
        # TODO: return headers from `prepped`.
        globals().update(locals())
        with httpx.Client() as client:
            return client.send(request)  
    return call

