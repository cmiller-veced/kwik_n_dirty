
sample_query_params = {
    'productId': 'ZFP',
    #        'typeId': 'TTTTTT',
    'zoneId': 'WYZ433',
    'stationId': 'CO100',
    #        'locationId': 'LLLLLL',
}


active_alerts = {
    'good': [
        { 'area': ['WY'], 'limit':   50, },
        { 'area': ['CO', 'KS', 'PK', 'PH'] },

        #        { 'xxxx':   'yyyyyyy', },    # additionalProperties permitted
        # but rejected by endpoint    400 Bad Request

        #        { 'zoneId':   'xxxxxx', },    # additionalProperties permitted
        # but rejected by endpoint    400 Bad Request

        { 'status':   ['actual', 'test'], }, 
        { 'message_type':   ['alert', 'cancel'], }, 
        { 'event':   ['Hard Freeze Warning', 'Dense Fog Advisory'], }, 
    ],
    'bad': [ 
            #        { 'limit':   '100', },
        # but accepted by endpoint
        { 'status':   ['xxxxxx'], }, 
    ],
}

# AHA!    brainwave!!!    Must take action to distinguish different error types
# in the test code.
# And distinguish validation error from endpoint error.
# for example with this ill-behaved endpoint ....
# /zones/forecast/{zoneId}/stations
zones_and_limits = {
    'good': [
        #{ 'zoneId': 'WYZ433', },   # 400 Bad Request
        { 'zone': 'WYZ433', },   # 400 Bad Request
        #        {  },   # valid but 500 Internal Server Error
        #        {
            #            'zoneId': 'WYZ433', 
            #    'limit':   50,
            #        },
            #        { 'zoneId': 'WYZ433', },   # valid but 400 Bad Request

            #            { 'limit':   5, },    # 500 error
        # TODO: investigate
        # 500 errors from /zones/forecast/{zoneId}/stations
        #        { 'xxxx':   'yyyyyyy', },    # additionalProperties permitted
    ],
    'bad': [ 
        { 'limit':   '100', },
        { 'zoneId':   'xxxxxx', },
    ],
}

zones = {
    'good': [
        #        { 'zone': 'WYZ433', },
        #{ 'zoneId': 'WYZ433', },
        #{ 'xxxx':   'yyyyyyy', },    # additionalProperties permitted
    ],
    'bad': [ 
        { 'zoneId':   'xxxxxx', },
    ],
}

start_end_limit = {
    'good': [
        {
            'start': '2024-09-17T18:39:00+00:00', 
            'end':   '2024-09-18T18:39:00+00:00',
            'limit':   50,
        },
        { 'start': '2024-09-17T18:39:00+00:00', },
        { 'end': '2024-09-17T18:39:00+00:00', },
        { 'limit':   50, },
        {  },
        {
            'start': '2024-09-17T18:39:00+00:00', 
            'end':   '2024-09-18T18:39:00+00:00',
            'limit':   '100', 
        },

        #        { 'start': '20240000-09-17T18:39:00+00:00', },
        # but rejected by endpoint    400 Bad Request

        #        { 'start': 'xxxxxxxx', },
        # but rejected by endpoint    400 Bad Request

        #        { 'x': 'yyyyyyy', },
        # but rejected by endpoint    400 Bad Request

    ],
    'bad': [ 
    ],
}

type_ids = {
    'good': [
        #        { 'typeId': 'ZFP', },
        #{ 'typeId': 'yyyyyyy', },
        #'ZFP', 'x', 1, {}, []      # anything goes!!!!!!!!!!!
        # but rejected by endpoint    400 Bad Request
    ],
    'bad': [ 
    ],
}

product_ids = {
    'good': [

        #        { 'productId': 'ZFP', },
        # but rejected by endpoint    400 Bad Request

        #        { 'productId': 'xxxxxx', },
        # but rejected by endpoint    400 Bad Request

        #        'ZFP', 'x', 1, {}, []      # anything goes!!!!!!!!!!!

    ],
    'bad': [ 
    ],
}

test_parameters = {
    '/alerts/active': active_alerts ,
    '/products/{productId}': product_ids ,
    '/products/types/{typeId}': type_ids ,
    '/stations/{stationId}/observations': start_end_limit ,
    '/zones/forecast/{zoneId}/observations' : zones,
    '/zones/forecast/{zoneId}/stations' : zones_and_limits,
} 


