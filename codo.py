import pandas as pd
base = pd.read_pickle('pickles/base.pkl')

idioma = 'es' # Opciones: es (español), en (inglés)

from funciones import obtener_stop_words
stop_words = obtener_stop_words(idioma)

data = base['lemas'].tolist()

from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(
    max_df=0.5,
    min_df=5,
    stop_words=stop_words,
)

X_tfidf = vectorizer.fit_transform(data) # matriz vectorizada con Tf-idf

from sklearn.cluster import KMeans
km = KMeans(init="k-means++", n_init=10, random_state=42) # objeto K-means

from sklearn.decomposition import TruncatedSVD
svd = TruncatedSVD(n_components=100, random_state=42) # objeto de reducción de dimensionalidad
X_reduced = svd.fit_transform(X_tfidf)  # matriz reducida

from yellowbrick.cluster import KElbowVisualizer
# Visualizador
visualizer = KElbowVisualizer(km, k=(2, 20), force_model=True) # objeto de visualización

visualizer.fit(X_reduced) # carga los datos
visualizer.show()