# valid UniProtKB accession

valid_accession = [
    { 'accession': 'A2BC19', },
    { 'accession': 'P12345', },
    { 'accession': 'A0A023GPI8', },
    { 'accession': 'P04637', },
]
bad_key = [{'x':'xxxxxxx',},]
        
#        { 'accession': 'P62988', },    # 404
proteins = {
    'good': valid_accession + [ 
        {},
        { 'accession': 'xxxxxxxx', },
    ],
    'bad': bad_key
}

proteins_accession = {
    'good': valid_accession,
    'bad': bad_key + [{}],
}

epitope = proteins

proteome = {
    'good': [
        { 'upid': 'UP000005640', },    # but empty result
    ],
    'bad': proteins['bad'],
}

das_s4entry = {
    'good': [{}, ],
    'bad': [{'x':''}],
}

uniparc_sequence = {
    'good': [
        {'rfActive': 'true'}, 
        {'rfActive': 'false'}, 
        {'rfDbid': 'AAC02967,XP_006524055'}, 
        {'rfDdtype': 'EMBL,RefSeq,Ensembl'}, 
             
     ],
    'bad': [
        {'rfActive': 'xxxxxxx'}, 
        {'rfTaxId': 'xxxxxx'}, 
        {'x': 'xxxxxx'}, 
    ],
}

hgvs_examples = ["NM_000551.3", "NC_000012.12"]  # bad request
hgvs_examples = ["c.88+2T>G",]  # invalid

# https://hgvs-nomenclature.org/stable/recommendations/grammar/
hgvs = {
    'good': [{'hgvs': thing} for thing in hgvs_examples],
    'bad': bad_key + [{},],
}


test_parameters = {
    '/proteins': proteins ,
    '/proteins/{accession}': proteins_accession ,
#    '/antigen/{accession}': antigen ,
    '/epitope': epitope ,
    '/proteomes': proteome ,
    '/proteomes/{upid}': proteome ,
    '/proteomics': proteome ,

   '/das/s4entry': das_s4entry ,               # patched
   '/uniparc/sequence': uniparc_sequence ,     # post
#    '/variation/hgvs/{hgvs}': hgvs ,
} 

