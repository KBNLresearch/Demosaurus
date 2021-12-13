from lxml import etree
from collections import defaultdict
import pandas as pd

global to_obtain
to_obtain = [
    {'table': 'publication_basicinfo',
     'columns': {
         'titelvermelding': lambda record: record.find('./p021A/fa').text,
         'verantwoordelijkheidsvermelding': lambda record:
         ';'.join(bit.text for bit in
                  [record.find('./p021A/fh')]
                  + record.findall('./p021A/fj')),
         'taal_publicatie': lambda record: record.find('./p010-/fa').text,
         'taal_origineel': lambda record: record.find('./p010-/fc').text,
         'land_van_uitgave': lambda record: record.find('./p019-/fa').text,
         'isbn': lambda record:
         ['978' + isbn.text if len(isbn.text) == 10 else isbn.text  # map ISBN-10 to ISBN-13 NB: TODO - recalculate checksum and convert to int (not possible now because ISBN-10 may contain 'X')
          for isbn in [record.find('./p004A/f0'), record.find('./p004A/fA'), '']
          if isbn is not None]  # use non-null values only
         [0],  # get the first valid isbn (if multiple are available)
         'jaar_van_uitgave': lambda record: int(record.find('./p011-/fa').text),
         'uitgever': lambda record: record.find('./p033A/fn').text,
         'uitgever_plaats': lambda record: record.find('./p033A/fp').text,
     }
     },
    {'table': 'publication_brinkman',
     'xpath': lambda record: record.findall('./p044Z'),
     'columns': {
         'term_identifier': lambda x: x.find('f9').text,
         'rank': lambda x: int(x.attrib['nr'])
     }
     },
    {'table': 'publication_CBK_genre',
     'xpath': lambda record: record.findall('./p044J'),
     'columns': {
         'term': lambda x: x.find('fa').text,
         'rank': lambda x: int(x.attrib['nr'])
     }
     },
    {'table': 'publication_CBK_thema',
     'xpath': lambda record: record.findall('./p044I'),
     'columns': {
         'term': lambda x: x.find('fa').text,
         'rank': lambda x: int(x.attrib['nr'])
     }
     },
    {'table': 'publication_NUGI_genre',
     'columns': {
         'term_identifier': lambda record: int(record.find('./p045O/fa').text),
     }
     },
    {'table': 'publication_NUR_rubriek',
     'columns': {
         'term_identifier': lambda record: int(record.find('./p045B/fa').text),
     }
     },
    {'table': 'publication_contributors',
     'xpath': lambda record: record.findall('./p028A') + record.findall('./p028B') + record.findall('./p028C'), #primary, co, secondary
     'columns': {
         'familyname': lambda x: x.find('fa').text,
         'prefix': lambda x: x.find('fc').text,
         'firstname': lambda x: x.find('fd').text + ''.join([' '+addition.text for addition in x.findall('fe')]),
         'title': lambda x: x.find('ff').text,
         'author_ppn': lambda x: x.find('f9').text,
         'role': lambda x: x.find('fB').text,
         'rank': lambda x: int(x.attrib['nr']) if 'nr' in x.attrib else 0
     }
     },
    {'table': 'publication_annotations',
     'columns': {
         'annotation': [
             lambda record: record.find('./p037A/fT').text,
             lambda record: record.find('./p037B/fT').text,
             lambda record: record.find('./p037E/fT').text,
             lambda record: record.find('./p020I/fa').text,
             lambda record: record.find('./p047D/fa').text,
             lambda record: record.find('./p020G/fa').text,
             lambda record: record.find('./p047I/fa').text,
             lambda record: record.find('./p020F/fa').text,
             lambda record: record.find('./p020A/fa').text,
             lambda record: record.find('./p047K/fa').text,
             lambda record: record.find('./p047L/fa').text,
         ],
         'kind': [
             lambda x: 'annotatie_alg',  # 4201
             lambda x: 'annotatie_alg2',  # 4202
             lambda x: 'annotatie_editie',  # 4203
             lambda x: 'annotatie_bibliografie',  # 4204
             lambda x: 'annotatie_inhoud',  # 4205
             lambda x: 'annotatie_taal',  # 4206
             lambda x: 'annotatie_samenvatting_inhoudsopgave',  # 4207
             lambda x: 'annotatie_verschijningsfrequentie',  # 4208
             lambda x: 'annotatie_karakteriserendegegevens',  # 4209
             lambda x: 'annotatie_analytisch_volw',  # 4600
             lambda x: 'annotatie_analytisch_jeugd'  # 4601
         ]
     }
     },
    {'table': 'publication_koepeltitel',
     'columns': {
         'koepel_ppn': lambda record: record.find('./p021A/f9').text,
     }
     }
]

global dfs
dfs = {item['table']: pd.DataFrame(columns=['publication_ppn'] + list(item['columns'].keys())) for item in to_obtain}

def obtain_for_record(record, verbose=True, ppn_list = []):
    ppn = record.find('./p003-/f0').text
    if len(ppn_list)>0 and ppn not in ppn_list:
        return # not a relevant PPN: skip
    for item in to_obtain:
        d = defaultdict(list)
        if 'xpath' in item.keys():  # repeatable metadata field: get all occurrences
            for occurrence in item['xpath'](record):
                for column, lambda_x in item['columns'].items():
                    value = None
                    try:
                        value = lambda_x(occurrence)
                    except (AttributeError, KeyError):
                        if verbose:
                            print('Couldnt obtain', item['table'], column, 'for PPN', ppn)
                    except Exception as e:
                        print('Error obtaining', item['table'], column, 'for PPN', ppn)
                        print(e)
                    d[column].append(value)
        else:  # non-repeatable field(s)
            for column, lambda_xs in item['columns'].items():
                if type(lambda_xs) is not list:
                    lambda_xs = [lambda_xs]
                for lambda_x in lambda_xs:
                    value = None
                    try:
                        value = lambda_x(record)
                    except AttributeError:
                        if verbose:
                            print('There is no', column, 'for PPN', ppn)
                    except Exception as e:
                        print('Error obtaining', item['table'], column, 'for PPN', ppn)
                        print(e)
                    d[column].append(value)
        if len(d)>0:
            df = pd.DataFrame(d).dropna(how='all')     # drop completely empty rows
            if type(item['columns'][column]) is list:  # annotations: drop rows with any missing field
                df = df.dropna()
            df['publication_ppn'] = ppn
            dfs[item['table']] = dfs[item['table']].append(df, ignore_index=True)

def read_pica_file(fname):
    tree = etree.parse(fname)
    return tree.getroot()

def obtain_dataframes(pica_file, head=-1, ppn_list = []):
    root = read_pica_file(pica_file)
    if head < 0:
        head = len(root)
    for record in root[:head]:
        obtain_for_record(record, False, ppn_list)
    return dfs

