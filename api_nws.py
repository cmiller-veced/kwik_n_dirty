import json

import httpx      # follow up to requests
import jsonref     # cross platform
from jsonschema import (     # cross platform
    Draft7Validator,
    FormatChecker,
)

from info import local
from tools import (
    raw_swagger, 
    endpoint_names,
    insert_endpoint_params,
)
from test_data_nws import test_parameters, sample_query_params

# TODO: fancy validators
# eg start_date < end_date


def schema_trans(schema_list):
    return {'properties': {thing['name']: thing['schema'] for thing in schema_list} }


def nws_validator(endpoint):
    """Return a function to validata parameters for `endpoint`.
    >>> params = dict(x=1)
    >>> assert nws_validator('/foo/{bar}/bat')(params) is True
    >>> is_valid = nws_validator('/foo/{bar}/bat')
    >>> assert is_valid(params) is True
    # TODO: consider name change.
    """
    rs = raw_swagger(local.swagger.nws)                              # global
    with_refs = jsonref.loads(json.dumps(rs))
    thing = with_refs['paths'][endpoint]
    vinfo = thing['parameters'] if 'parameters' in thing else thing['get']['parameters']
    schema = schema_trans(vinfo)     # NWS-specific
    assert list(schema.keys()) == ['properties']
#    print(endpoint, list(schema['properties'].keys()))
    is_valid = lambda ob: Draft7Validator(schema, format_checker=FormatChecker()).is_valid(ob)
    is_valid = Draft7Validator(schema, format_checker=FormatChecker()).is_valid
#    is_valid.endpoint = endpoint
 #   is_valid.schema = schema
    return is_valid


def nws_call(endpoint, params=None):
    with httpx.Client(base_url=local.api_base.nws) as client:
        r = client.get(endpoint, params=params)
        assert r.status_code == 200
    return r.json()


# test
# ############################################################################
from functools import lru_cache

def nws_validate_and_call():
  try:
    rs = raw_swagger(local.swagger.nws)                              # global
    with httpx.Client(base_url=local.api_base.nws) as client:
        for ep in endpoint_names(rs):
            is_valid = nws_validator(ep)
            print(ep)
#            print(is_valid.endpoint)
            ep0 = ep
            if ep in test_parameters:
                things = test_parameters[ep]
                ep = insert_endpoint_params(ep, sample_query_params)
                if ep0 != ep:
                    print('   calling .............', ep)
                for params in things['good']:
                    assert is_valid(params)
                    print('   ok good', params)
                    r = client.get(ep, params=params)
                    assert r.status_code == 200
                for params in things['bad']:
                    assert not is_valid(params)
                    print('   ok bad', params)
                    r = client.get(ep, params=params)
                    assert r.status_code != 404    # Bad endpoint
                    assert r.status_code in [400, 500]    # Bad Parameter
                    # or Server Error
                    # 500 from /zones/forecast/{zoneId}/stations
                    # with {'limit': '100'}
  finally:
    globals().update(locals())



# NWS data ##################################################################


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
    globals().update(locals())
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
    globals().update(locals())



# aside
# ############################################################################

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


