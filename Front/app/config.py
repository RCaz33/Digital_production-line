

allowed_email_pattern = r'@something.com'  # Example pattern: email must end with @example.com
allowed_emails=['a','list','of','allowed','emails']

matieres_premieres = ['a','list','of','raw','RE1','RE2']
codes_MP_CW = [f'CW_00{i}' for i in range(1,10)]

Techniciens_CW = ['FB','IT','CD','JP','MM','RS','WL','LB','LC','TB']
Techniciens_CW_dict=dict(zip(Techniciens_CW,range(1,len(Techniciens_CW)+1)))

codes_MP_CW = dict({'Carbone': 'CW_001',
                    'Potassium': 'CW_002',
                    'YY': 'CW_003',
                    'Viscosant':'code_viscosant',
                    'RE1':'code_resine1',
                    'RE2':'code_resine2'})

unitees = ['Kg','L']

Produits_CW = ['W2','W2NC','W3','W3NC','W10','W10NC','EpoF','EpoC']


clients = ['Client 1 ',
          'Client 1 UK',
          'Client 1 Italy',
          'Client 2',
          'Client 3',
          'Client 4 Site 1',
          'Client 4 Site 2']


ref_CW_matiere_premiere=dict({'RE1':'EPO1',
                              'RE2':'EPO3',
                              '...':'...',
                              })
    
ref_CW_produit=dict({'P1':'CW-GL-A-01-A1-T1',
                     '...':'...',
                     })
    
default_batch = {'K': 'na', 'C': 'na', 'YY': 'na', 'XX': 'na'}