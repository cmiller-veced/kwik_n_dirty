from datetime import datetime
from info import local
from tools import ( LocalValidationError,)
from nother import dv, dcall
# TODO: change some of the `other` names.


class DateOrderError(LocalValidationError): pass

class ValidDataBadResponse(LocalValidationError): pass


def local_validate(params):
    """Catch data problems missed by the schema.
    # eg start_date > end_date
    params = {
        'start': '2024-09-17T18:39:00+00:00', 
        'end':   '2024-09-18T18:39:00+00:00',
    }
    """
    fmt = '%Y-%m-%dT%H:%M:%S+00:00'
    if 'start' in params and 'end' in params:
        start = params['start']
        end = params['end']
        if datetime.strptime(start, fmt) > datetime.strptime(end, fmt): 
            raise DateOrderError(start, end)


def altered_raw_swagger(jdoc):
    """Alter raw data to conform with local code assumptions.
    This function takes a swagger doc as a json and returns json.
    """
    for endpoint in jdoc['paths']:
        epdoc = jdoc['paths'][endpoint]
        assert 'get' in epdoc
        assert 'parameters' in epdoc['get']
        if 'parameters' in epdoc:
            eprams = epdoc.pop('parameters')
            jdoc['paths'][endpoint]['get']['parameters'].extend(eprams)
    return jdoc

        
def head_func(endpoint, verb):
    """nws requires user-agent header.   Returns 403 otherwise.
    """
    return {'user-agent': 'python-httpx/0.27.2'}


class config:
    swagger_path = local.swagger.nws
    api_base = local.api_base.nws
    alt_swagger = altered_raw_swagger
    head_func = head_func
    validate = local_validate


_validator = dv(config)
call = dcall(config)


# test
# ############################################################################
from functools import lru_cache
from pprint import pprint
from collections import defaultdict
from tools import ( raw_swagger, )
import nother
from nother import NonDictArgs
from test_data_nws import test_parameters   #, sample_query_params

# TODO: clarify messaging.
def validate_and_call():
  try:
    bad_param_but_ok = defaultdict(list)
    good_param_not_ok = defaultdict(list)
    jdoc = raw_swagger(local.swagger.nws)  # TODO: pass flag for deref vs not.?
    jdoc = jsonref.loads(json.dumps(jdoc))
    paths = altered_raw_swagger(jdoc)['paths']
    for endpoint in paths:
        for verb in paths[endpoint]:
            #            assert verb in 'get post'
            #            assert verb in 'get post'
            validator = _validator(endpoint, verb)
            print(endpoint, verb)
            if endpoint in test_parameters:
                things = test_parameters[endpoint]
                for params in things['good']:
                    if not validator.is_valid(params):
                        validator.validate(params)

                    print('   ok good valid', params)
                    response = call(endpoint, verb, params)
                    if not response.is_success:
                        good_param_not_ok[(endpoint, verb)].append(params)
                        raise ValidDataBadResponse(params)
                    if response.is_success:
                        print('   ok good call')
                for params in things['bad']:
                    assert not validator.is_valid(params)
                    print('   ok bad NOT valid', params)
                    try:
                        # TODO: re-extract prepped args.   ?????
                        # NO.
                        # Maybe.
                        # But first get accustomed to debugging as-is.
                        # Should have better visibility there.
                        response = call(endpoint, verb, params)
                    except NonDictArgs:
                        break
                    if response.is_success:
                        bad_param_but_ok[(endpoint, verb)].append(params)
  finally:
    bad_param_but_ok = dict(bad_param_but_ok)
    good_param_not_ok = dict(good_param_not_ok)
    globals().update(locals())


# NWS data ##################################################################


def nws_call(endpoint, params=None):
    return call(endpoint, 'get', params).json()


@lru_cache
def alert_types():
    return nws_call('/alerts/types')['eventTypes']


@lru_cache
def stations():
    js = nws_call('/stations')
    counties = set()                           # thing of interest
    for feat in js['features']:
        if 'county' in feat['properties']:
            counties.add(feat['properties']['county'])
    typ = [d['properties']['@type'] for d in js['features']]
    typ = sorted(list(set(typ)))
    assert typ == ['wx:ObservationStation']             # thing of interest
    ids = [d['properties']['stationIdentifier'] for d in js['features']]
    oz = js['observationStations']
    assert type(oz) is list
    assert oz[-1].endswith(ids[-1])   # duplicated info
    return ids


@lru_cache
def radar_stations():
    js = nws_call('/radar/stations')
    typ = [d['properties']['@type'] for d in js['features']]
    typ = sorted(list(set(typ)))
    assert typ == ['wx:RadarStation']  # thing of interest
    station_types = [d['properties']['stationType'] for d in js['features']]
    station_types = sorted(list(set(station_types)))
    assert station_types == ['Profiler', 'TDWR', 'WSR-88D']  # thing of interest
    return [d['properties']['id'] for d in js['features']]


@lru_cache
def zone_ids():
    js = nws_call('/zones')
    atypes = [d['properties']['@type'] for d in js['features']]
    atypes = sorted(list(set(atypes)))
    ttypes = [d['properties']['type'] for d in js['features']]
    ttypes = sorted(list(set(ttypes)))
    assert atypes == ['wx:Zone']
    assert ttypes == ['coastal', 'county', 'fire', 'offshore', 'public']
    ids = [d['properties']['id'] for d in js['features']]
    return sorted(list(set(ids)))


@lru_cache
def product_codes():
    js = nws_call('/products/types')
    context = js['@context']
    things = js['@graph']
    return [d['productCode'] for d in things]


# ^ NWS data ^ ###############################################################


# Fetch a data set suitable for a pandas dataframe.
# ############################################################################
import pandas      # similar to R data frames


from jinja2 import Environment, select_autoescape 
# TODO: remove in favor of newer thing.
# endpoint_QUERY_params
def insert_endpoint_params(endpoint, parameters):
    if not '{' in endpoint:
        return endpoint
    env = Environment(autoescape=select_autoescape())
    template = env.from_string(templatified(endpoint))
    return template.render(**parameters)



def nws_series():
  try:
    """ Get a series of observations suitable for putting in a pandas DF,
    and then a jupyter notebook.
    """
    # Data
    ep1 = '/stations/{stationId}/observations'
    # TODO: validate stationId ??????
#'089SE', '0900W'
    stationId = 'KRCM'   # OK
    stationId = 'CO100'   # OK
    # NOTE  stationId cannot go in params.
    params = {                                # OK
        'start': '2024-09-22T23:59:59+00:00', 
        'end':   '2024-09-23T23:59:59+00:00', 
        'limit':   50,
    }

    # Validate params
    assert nws_validator(ep1)(params)

    # Insert stationId into endpoint path
    ep = insert_endpoint_params(ep1, locals())

    import httpx      # follow up to requests
    # Call the endpoint and verify status_code.
    with httpx.Client(base_url=local.api_base.nws) as client:
        r = client.get(ep, params=params)
        assert r.status_code == 200

    # Extract desired data from response.
    final = []
    feats = r.json()['features']
    for ft in feats: 
        pt = ft['properties']
        for key in [ '@id', '@type', 'elevation', 'station', 'rawMessage', 'icon', 'presentWeather', 'cloudLayers', 'textDescription', ]:
            pt.pop(key)
        for key in pt:
            if type(pt[key]) is dict:
                pt[key] = pt[key]['value']
        final.append(pt)

    # Convert to dataframe.
    df = pandas.DataFrame(final)
#    assert df.shape == (50, 15)
    assert df.shape[1] == 15
    return df
  finally:
    pass


# aside
# ############################################################################

import json
import jsonref     # cross platform
def get_component_schemas_nws():    # NWS
    rs = raw_swagger(local.swagger.nws)
    with_refs = jsonref.loads(json.dumps(rs))
    components = with_refs['components']
    for key in ['responses', 'headers', 'securitySchemes']:
        components.pop(key)
    parameters = components['parameters']
    components['parameters'] = {key: parameters[key]['schema'] for key in parameters}
    return components

# exp
class NWS:
    product_codes = product_codes()
    zone_ids = zone_ids   # NOTE  zone_ids is very much like a static method.
    # Which means a class consisting of all static methods is nothing more than
    # a namespace.
    # I think the same is true for class methods. IOW, a class having only
    # static and class methods is a namespace.  Nothing more.
    # and
    # If you think about it, you realize that neither class nor static methods
    # operate on instance data.
    # Thus they are really a different animal than the usual image of methods as
    # operating on client data.
    # NO
    #
    zone_ids = classmethod(zone_ids) 
    # TODO: but wait!!!!!!!
    # both defs of zone_ids give an error...
    # Traceback (most recent call last):
    # File "<stdin>", line 1, in <module>
    # TypeError: zone_ids() takes 0 positional arguments but 1 was given
    # thus, zone_ids MUST be defined as...
    @classmethod
    def zone_ids(self):
        return zone_ids()
    # which is quite verbose.
    # The way product_codes operates seems better.

nws = NWS()


heads = {'host': 'api.weather.gov', 'accept': '*/*', 'accept-encoding': 'gzip, deflate', 'connection': 'keep-alive', 'user-agent': 'python-httpx/0.27.2'}


if __name__ == '__main__':
    validate_and_call()
