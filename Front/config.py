

allowed_email_pattern = r'@carbon-waters.com'  # Example pattern: email must end with @example.com
allowed_emails=['a@carbon-waters.com','b@carbon-waters.com','c@carbon-waters.com']

matieres_premieres = ['Carbone', 'Potassium','THF']
codes_MP_CW = [f'CW_00{i}' for i in range(1,10)]

Techniciens_CW = ['FB','IT','CD','JP','MM','RS','WL','LB','LC','TB']


codes_MP_CW = dict({'Carbone': 'CW_001',
                    'Potassium': 'CW_002',
                    'THF': 'CW_003'})

unitees = ['Kg','L']

Produits_CW = ['W2','W2NC','W3','W3NC','W10','W10NC','EpoF','EpoC']


clients = ['Client 1 ',
          'Client 1 UK',
          'Client 1 Italy',
          'Client 2',
          'Client 3',
          'Client 4 Site 1',
          'Client 4 Site 2']


ref_CW_matiere_premiere=dict({'Epikote1001X75':'EPO1',
                              'Epikote827':'EPO3',
                              'RTM6-2':'EPO5',
                              'SikaBiresinCR87':'EPO6',
                              'ELIUM150':'EPO7',
                              'LY564':'EPO8',
                              'PY306':'EPO9',
                              'LY3508':'EPO10',
                              'Resoltechnon-CMR':'EPO11',
                              'ResoltechCMR':'EPO12',
                              'Thermoplastique':'TP',
                              'PLA':'TP1',
                              'PET':'TP2',
                              'PP':'TP3',
                              'THF':'code_THF',
                              'Potassium':'code_K',
                              'Carbone':'code_C'})
    
ref_CW_produit=dict({'W1':'CW-GL-A-01-A1-T1',
                     'W2':'CW-GL-B-02-A1',
                     'W3':'CW-GL-D-02-A1',
                     'W3NC':'CW-GL-DX-02-A1',
                     'W10':'CW-GL-E-02-A1',
                     'W10NC':'CW-GL-EX-02-A1',
                     'W20':'CW-GL-F-02-A1',
                     'W20NC':'CW-GL-FX-02-A1',
                     'EpoR':'CW-EPO3-D-01-A1',
                     'EpoF':'CW-EPO3-F-01-A1',
                     'EpoC':'CW-EPO1-D-01-A1'})
    