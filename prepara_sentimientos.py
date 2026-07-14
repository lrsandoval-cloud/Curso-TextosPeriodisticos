import pandas as pd
from nltk.tokenize import sent_tokenize

#import nltk
#nltk.download('punkt_tab')

idioma = 'es' # Opciones: es (español), en (inglés)

base = pd.read_pickle('pickles/base.pkl')

columnas = ['oracion', 'label', 'score', 'columna', 'medio','fecha', 'idnota']
sentimientos = pd.DataFrame(columns=columnas)

from transformers import pipeline
classifier = pipeline('sentiment-analysis', model="nlptown/bert-base-multilingual-uncased-sentiment")

if idioma == 'es':
    lenguaje = 'spanish'
elif idioma == 'en':
    lenguaje = 'english'

rotulos = list(base['medio'].unique())
campos = ['titulo', 'copete', 'texto']

idnota = 1
for rotulo in rotulos:
    segmento = base.query("medio == '" + rotulo + "'")
    for i, row in segmento.iterrows():
        for campo in campos:
            if row[campo] is not None:
                toks = sent_tokenize(row[campo], lenguaje)
                for tok in toks:
                    if len(tok) < 512:
                        sentir = classifier(tok)
                        label = sentir[0]['label'][:1]
                        score = sentir[0]['score']
                        sentimientos.loc[len(sentimientos)] = {
                            'oracion' : tok,
                            'label' : label,
                            'score' : score,
                            'columna' : campo,
                            'medio' : row['medio'],
                            'fecha' : row['fecha'],
                            'idnota' : i
                        }
        print(i, row['titulo'])
        idnota += 1
        if i % 10 == 0:
            sentimientos.to_pickle('pickles/sentimientos.pkl')


sentimientos.to_pickle('pickles/sentimientos.pkl')
