

# valid UniProtKB accession

proteins = {
    'good': [
        { 'accession': 'A2BC19', },
        { 'accession': 'P12345', },
        { 'accession': 'A0A023GPI8', },
        { 'accession': 'P04637', },
#        { 'accession': 'P62988', },    # 404
        
    ],
    'bad': [ 
        [],
        'xxxxxxx',
        { 'accession': 'xxxxxxxx', },
    ],
}
#proteins['bad'] = []
proteins_accession = {
    'good': proteins['good'],
    'bad': [ ],
}

epitope = {
    'good': proteins['good'],
    'bad': proteins['bad'],
}

proteome = {
    'good': [
        { 'upid': 'UP000005640', },    # but empty result
    ],
    'bad': proteins['bad'],
}


hgvs_examples = ["NM_000551.3", "NC_000012.12"]  # bad request
# https://hgvs-nomenclature.org/stable/recommendations/grammar/
hgvs = {
    'good': [{'hgvs': thing} for thing in hgvs_examples],
    'bad': [{}, ''],
}


test_parameters = {
    '/proteins': proteins ,
    '/proteins/{accession}': proteins_accession ,
#    '/antigen/{accession}': antigen ,
    '/epitope': epitope ,
    '/proteomes': proteome ,
    '/proteomes/{upid}': proteome ,
    '/proteomics': proteome ,
#    '/variation/hgvs/{hgvs}': hgvs ,
} 


