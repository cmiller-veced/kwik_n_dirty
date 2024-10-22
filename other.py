import json
import jsonref
from jsonschema import FormatChecker
import httpx

from tools import (dvalidator, raw_swagger, identity_func,
                   extract_from_dict_list,
                   retry_call,
                   )


def parameters_to_schema(parameters):
    pr = extract_from_dict_list(parameters, 'required')
    return {
        'required': [key for key in pr if pr[key]],
        'properties': extract_from_dict_list(parameters, 'schema'), 
        'additionalProperties': False, 
        'type': 'object', 
    }


# TODO: reorder args so we can default to foo=identity_func
# TODO: We do need the altered swagger here.
def dv(swagger_path, local_validate=identity_func, altered_raw_swagger=identity_func,):
    def validator(endpoint, verb='get'):
        """Return a validator for `(endpoint, verb)`.
        """
        jdoc = jsonref.loads(json.dumps(raw_swagger(swagger_path)))
        jdoc = altered_raw_swagger(jdoc)
        globals().update(locals())
        parameters = jdoc['paths'][endpoint][verb]['parameters']
        schema = parameters_to_schema(parameters)
        return dvalidator(local_validate)(schema, format_checker=FormatChecker())
    return validator


# TODO: I think we do NOT need altered_raw_swagger here.
# NO.
# I think we do need it because of
# location = extract_from_dict_list(paths[endpoint][verb]['parameters'], 'in')
# TODO: Is there some way to reduce the number of calls to altered_raw_swagger?
# or not really the number of calls, but the number of times it appears as
# a parameter.

class NonDictArgs(Exception): pass

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
#        paths = jsonref.loads(json.dumps(rs))['paths']
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
#        heads = headers(endpoint, verb) if headers else None
#        return (api_base + endpoint, verb, request_params, heads)
        return (api_base + endpoint, verb, request_params)
      finally:
        globals().update(locals())
    return prepped

# TODO: add something to add headers to a fiw random endpoints to illustrate.
# Maybe.
# TODO: no need to test with bad params????????//
# Because those should be caught by validation...


def dcall(local, head_func=None, altered_raw_swagger=identity_func):
    """
    """
    prepped = prep_func(local.api_base.nws, local.swagger.nws, altered_raw_swagger)
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

