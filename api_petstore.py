from collections import defaultdict
from test_data_petstore import test_parameters
import json

import httpx
import jsonref
import jsonschema
from jsonschema import ( Draft7Validator, FormatChecker, validate)

from tools import (
    raw_swagger, 
    local,        # not a tool.  It is data.
    endpoint_names,
    insert_endpoint_params,
    recur, delete_key, DotDict, namespacify,
)

from copy import deepcopy
from pprint import pprint
from demo_class import validated_for_dict
import types
from types import SimpleNamespace
import pytest

header = {'accept: application/json'}
sample_data = {
    'username': 'merlin', 
    'file': 'foofile', 
    'api_key': 'foobar', 
    'additionalMetadata': 'foof', 
    'name': 'yourName', 
#    'status': 'sold', 
    'status': ['sold'], 
    'password': 'xxxxx', 
    'petId': 99, 
    'orderId': 9, 
    'tags': ['foo']
}


# schema fetching
def get_definition_schemas_petstore():
    rs = raw_swagger(local.swagger.petstore)
    with_refs = jsonref.loads(json.dumps(rs))
    defs = with_refs['definitions']
    assert list(defs) == ['ApiResponse', 'Category', 'Pet', 'Tag', 'Order', 'User']
    return defs
    # The Pet schema is a good one.
    # What a Pet object should conform to.


def get_endpoint_locations():
    # by subtracting
    rs = raw_swagger(local.swagger.petstore)       # 
    top_level_keys = 'swagger info host basePath tags schemes securityDefinitions externalDocs definitions'.split()
    ep_keys = 'summary description operationId consumes produces responses security'.split()
    param_keys = 'required schema type deprecated'.split()
    schema_keys = 'format maximum minimum items collectionFormat'.split()
    all_keys = top_level_keys + ep_keys + param_keys + schema_keys
    for key in all_keys:
        delete_key(rs, key)

    # transform list-of-dicts to dict.
    jdoc = rs
    for path in jdoc['paths']:
        for verb in jdoc['paths'][path]:
            assert len(jdoc['paths'][path][verb]) == 1
            assert 'parameters' in jdoc['paths'][path][verb]
            new = {}
            for param in jdoc['paths'][path][verb]['parameters']:
                new.update({param['name']: param['in']})
            jdoc['paths'][path][verb]['parameters'] = new
    return rs


def test_endpoint_locations():
  try:
    jdoc = get_endpoint_locations()['paths']
    for path in jdoc:
        for verb in jdoc[path]:
            assert len(jdoc[path][verb]) == 1
            assert 'parameters' in jdoc[path][verb]
            print(path, verb, jdoc[path][verb]['parameters'])
  finally:
    globals().update(locals())


def get_schemas():
    # by subtracting
    rs = raw_swagger(local.swagger.petstore)       # 
    with_refs = jsonref.loads(json.dumps(rs))
    rs = with_refs
    top_level_keys = 'swagger info host basePath tags schemes securityDefinitions externalDocs'.split()
    ep_keys = 'operationId consumes produces responses security'.split()
    param_keys = []
    schema_keys = ['xml']
    all_keys = top_level_keys + ep_keys + param_keys  + schema_keys
    for key in all_keys:
        delete_key(rs, key)
    return rs
def test_get_schemas():
  try:
    jdoc = get_schemas()    #['paths']
    assert sorted(list(jdoc)) == ['definitions', 'paths']
    jd = jdoc['definitions']
    jp = jdoc['paths']
    assert list(jd) == ['ApiResponse', 'Category', 'Pet', 'Tag', 'Order', 'User']
    assert list(jp) == ['/pet/{petId}/uploadImage', '/pet', '/pet/findByStatus', '/pet/findByTags', '/pet/{petId}', '/store/inventory', '/store/order', '/store/order/{orderId}', '/user/createWithList', '/user/{username}', '/user/login', '/user/logout', '/user/createWithArray', '/user']
  finally:
    globals().update(locals())


def parameter_list_to_schema(parameter_list):
    d = {}
    for pdict in parameter_list:
        td = {}
        if 'type' in pdict:
            td['type'] = pdict['type']
        if 'format' in pdict:
            td['format'] = pdict['format']
        if 'in' in pdict:
            td['in'] = pdict['in']
        d[pdict['name']] = td
    d['type'] = 'object'
    d['required'] = [pd['name'] for pd in parameter_list if pd['required']]
    return d


def test_parameter_list_to_schema():
    s = parameter_list_to_schema(es['parameters'])
    validator = Draft7Validator(s, format_checker=FormatChecker())
    x = { 'petId': 1234, }
    assert validator.is_valid(x)


# working
if 0:      # insert info into request
    interface_schema = dict(
        type='object',
        additionalProperties=False,
        #    required = ['httpx_request', 'endpoint_info'],
        required = ['endpoint_info'],
        properties=dict(
            #        httpx_request=dict( type='string',),
            # Here we have a shortcoming of jsonschema.
            # I want to specify that httpx_request must be httpx.Request object but
            # there's no way to do that in jsonschema.
            # TODO: maybe sometime, redo this validator in Pydantic so we can
            # specify httpx.Request.
            # But otoh, if something else ever gets passed in it will be really easy
            # to track down.
            httpx_request=dict(),
            endpoint_info=dict(
                required = ['endpoint', 'verb'],
                type='object',
                endpoint=dict( type='string',),
                verb=dict( type='string',),
                ),
            parameters=dict(
                type='object',
                body=dict( type='object',),
                headers=dict( type='object',),
                path=dict( type='object',),
                query=dict( type='array',),
            )
        )
    )


    class Combined(validated_for_dict(interface_schema)):
        def insert_to_request(self, httpx_request: httpx.Request):
            """
            """
            request = httpx_request
            parameters = self['parameters']
            info = self['endpoint_info']
            # TODO: put them together.
            return 'xxx'
     
    dx = dict(parameters=dict(query=[]), httpx_request='foof')  # OK
    dx = dict(
        parameters=dict(query=[]), 
        httpx_request=[],
        endpoint_info=dict(
            endpoint='/foo/bar/{bat}',
            verb='post',
        ),
    )  # OK
    dbad = dict(params=dict(query=[]))  # OK
    ##############
    ##############
    ok = Combined(dx)
    with pytest.raises(jsonschema.exceptions.ValidationError):
        db = Combined(dbad)
    okns = json.loads(json.dumps(ok), object_hook=DotDict)
    assert okns.parameters == {'query': []}
    assert okns.parameters.query == []
    assert okns.endpoint_info.verb == 'post'
    with pytest.raises(KeyError):
        ick = okns.insert_to_request()
    ick = ok.insert_to_request('req')


# schema fetching
def endpoint_schema(endpoint, verb):
    """Pull schema with some adjustments for internal inconsistency within the
    OpenAPI doc.
    AFII: adjust for internal inconsistency
    """
    jdoc = get_schemas()['paths']
    defs = get_schemas()['definitions']
    for ep in jdoc:
        for v in jdoc[ep]:
            if (endpoint, verb) == (ep, v):
                s = jdoc[endpoint][verb]

                # AFII
                if len(s['parameters']) == 1:
                    p = s['parameters'][0]
                    if p['in'] == 'body':
                        assert 'schema' in p
                        s = p['schema']
    # AFII
    if 'parameters' in s:
        if len(s['parameters']) > 1:
            s = parameter_list_to_schema(s['parameters'])
            print('yoohoo')
            print('yoohoo')
            print('yoohoo')
        elif len(s['parameters']) == 1:
            s = s['parameters'][0]
    return s


# working
def test_endpoint_schema_validation():
  try:
    """
    """
    endpoint_locations = get_endpoint_locations()['paths']
    # TODO: useit
    jdoc = get_schemas()['paths']
    for endpoint in jdoc:
        for verb in jdoc[endpoint]:
            es = endpoint_schema(endpoint, verb)
            loc = endpoint_locations[endpoint][verb]['parameters']

            print(endpoint, verb)
            print(es)
            print('---------------------------------------')
            print(loc)

            validator = Draft7Validator(es, format_checker=FormatChecker())
            samples = test_parameters[endpoint][verb]
            print('---', samples['good'])
            for thing in samples['good']:
                print('---', thing)
                assert validator.is_valid(thing)
                
                # OK.  Now we know it is valid.
                # Hit the endpoint to see if it works.
                (url, request_params) = populate_request(endpoint, verb, thing)
                request = httpx.Request(verb, url, **request_params)
                with httpx.Client(base_url=local.api_base.petstore) as client:   # 
                    response = client.send(request)  
                    assert response.is_success

#                if thing: gthing = thing
            for thing in samples['bad']: 
                assert not validator.is_valid(thing)
            # TODO: call the endpoint with the params
            # need other info from swagger.
            print()
  finally:
    globals().update(locals())


def populate_request(endpoint, verb, data):
  try:
    loc = get_endpoint_locations()['paths'][endpoint][verb]['parameters']
    thing = deepcopy(data)
    if type(thing) in [str, int]:
        assert len(loc) == 1
        (pname, ploc) = list(loc.items())[0]
        if ploc == 'path':
            endpoint = endpoint.replace(pname, str(thing)) .replace('{', '') .replace('}', '')
            url = local.api_base.petstore + endpoint   # cmn
            return (url, {})

    if loc == {'body': 'body'}:
        url = local.api_base.petstore + endpoint   # cmn
        return (url, dict(json=thing))

    request_params = {}
    query = {}
    form_data = {}
    kw = {}
    to_delete = []
    for param in thing:
        plocation = loc[param]
        print(plocation)
        if plocation == 'path':
            ep0 = endpoint
            ep1 = endpoint.replace(param, str(thing[param]))\
                    .replace('{', '') .replace('}', '')
            endpoint = ep1
            to_delete.append(param)
        elif plocation == 'query':
            query.update({param: thing[param]})
        elif plocation == 'formData':
            form_data.update({param: thing[param]})

#         if param == 'body':
#             assert 'body' ==  loc[param]
#             kw['json'] = thing['body']
#             to_delete.append(param)
    for pname in to_delete:
        thing.pop(pname)
    print(thing)
    if query:
        request_params.update({'params': query})
    if form_data:
        # request_params.update({'data': form_data})      # 415 Unsupported Media Type
        # request_params['headers'] = common.headers.form_data  # 500 Server Error
        """
        <body><h2>HTTP ERROR 500</h2>
<p>Problem accessing /v2/pet/1234/uploadImage. Reason:
<pre>    Server Error</pre></p><h3>Caused by:</h3><pre>javax.ws.rs.WebApplicationException: java.lang.IllegalArgumentException: Error parsing media type 'form-data'

{"id":3,"name":"rocky","photoUrls":[],"tags":[]}
otoh.
Apparently the petstore server is known to be buggy.
Probably not worth spending much time on debugging it.
        """
        form_data['id'] = 1234

        request_params.update({'json': form_data})      # 415 Unsupported Media Type
        request_params['headers'] = common.headers.content_type_json  # 
        # 415


#    if request_params['json']:
 #       request_params['headers'] = common.headers.content_type_json

    url = local.api_base.petstore + endpoint   # cmn
    return (url, request_params)
  finally:
    pass
#    globals().update(locals())


class common:
    class headers:
        content_type_json = {'Content-Type': 'application/json'}
        form_data = {'Content-Type': 'form-data'}


def petstore_validate_and_call1():
  try:
    # TODO: useit
    jdoc = get_schemas()['paths']
    for endpoint in jdoc:
        for verb in jdoc[endpoint]:
            es = endpoint_schema(endpoint, verb)
            print(endpoint, verb)
            print(es)
            validator = Draft7Validator(es, format_checker=FormatChecker())
            samples = test_parameters[endpoint][verb]
            for thing in samples['good']:
                assert validator.is_valid(thing)
                if thing:
                    gthing = thing
            for thing in samples['bad']: 
                assert not validator.is_valid(thing)
    return 
# TODO: useit
# goal:  Make it work like this...
    with httpx.Client(base_url=local.api_base.petstore) as client:   # 
        for endpoint in endpoint_names(rs):
            for verb in endpoint:
                for params in test_data['good']:
                    assert params_ok
                    load_params
                    send_params
                    assert it_worked
                for params in test_data['bad']:
                    assert params_NOT_ok
                    load_params
                    send_params
                    assert NOT_it_worked
  finally:
    pass

def endpoint_info(endpoint, verb):
    """Pull endpoint info relevant for the API call.
    """
    jdoc = get_schemas()['paths']
    for ep in jdoc:
        for v in jdoc[ep]:
            if (endpoint, verb) == (ep, v):
                s = jdoc[endpoint][verb]
    return None


def petstore_endpoint_verbs(endpoint):
    rs = raw_swagger(local.swagger.petstore)
    with_refs = jsonref.loads(json.dumps(rs))
    thing = with_refs['paths'][endpoint]
    return list(thing)

def petstore_endpoint_verb_details(endpoint, verb):
    rs = raw_swagger(local.swagger.petstore)
    with_refs = jsonref.loads(json.dumps(rs))
    thing = with_refs['paths'][endpoint][verb]
    return thing

