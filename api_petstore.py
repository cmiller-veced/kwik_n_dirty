from copy import deepcopy
import json

import jsonref

from tools import (
    raw_swagger, 
    local,        # not a tool.  It is data.
    common,        # not a tool.  It is data.
    delete_key,
)


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
        # request_params['headers'] = common.headers.content_type.form_data  # 500 Server Error
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
        request_params['headers'] = common.headers.content_type.json  # 
        # 415

#    if request_params['json']:
 #       request_params['headers'] = common.headers.content_type.json

    url = local.api_base.petstore + endpoint   # cmn
    return (url, request_params)
  finally:
    pass

