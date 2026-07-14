import pandas as pd
import spacy

modelo = 'es_core_news_sm'
base = pd.read_pickle('pickles/scielo_uy.pkl')

nlp = spacy.load(modelo)

base['lemas'] = ''

for i, row in base.iterrows():
    print(i, row['Título'])
    try:
        texto = row['Resumen']
        doc = nlp(texto)
    except ValueError:
        continue

    lemas = []
    for token in doc:
        if token.pos_ not in ['ADP', 'DET', 'PRON', 'NUM', 'CCONJ', 'SCONJ', 'PUNCT', 'SYM']:
            if not token.is_stop:
                lemas.append(token.lemma_.lower())
    base.loc[i, 'lemas'] = " ".join(lemas)


pd.to_pickle(base, 'pickles/scielo_uy.pkl')
