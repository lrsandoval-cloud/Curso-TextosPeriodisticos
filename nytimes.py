import requests
import pandas as pd
import time

# Configuración inicial
API_KEY = ""  # Colocar la clave generada
URL_BASE = "https://api.nytimes.com/svc/search/v2/articlesearch.json"

# Parámetros de búsqueda
# NYT utiliza la sintaxis Lucene
filtro_busqueda = '"artificial intelligence" AND (work OR job)'
fecha_inicio = "20170101"  # Formato AAAAMMDD
fecha_fin = "20260601"  # Formato AAAAMMDD

articulos_lista = []

#anios = ["2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
anios = ["2025", "2026"]

for anio in anios:
    print(f"--- Descargando año {anio} ---")

    for page in range(0, 5):
        print(f"Descargando página {page}...")

        params = {
            "fq": filtro_busqueda,  # Usamos fq para la lógica compleja
            "begin_date": f"{anio}0101",
            "end_date": f"{anio}1231" if anio != "2026" else "20260601",
            "page": page,
            "sort": "oldest",
            "api-key": API_KEY
        }

        response = requests.get(URL_BASE, params=params)

        if response.status_code == 200:
            data = response.json()
            docs = data.get("response", {}).get("docs", [])

            for doc in docs:
                info_articulo = {
                    "fecha": doc.get("pub_date"),
                    "titulo": doc.get("headline", {}).get("main"),
                    "texto" : "",
                    "abstract": doc.get("abstract"),
                    "copete": doc.get("snippet"),
                    "url": doc.get("web_url"),
                    "seccion": doc.get("section_name"),
                    "autor": doc.get("byline", {}).get("original"),
                    "medio" : "nyt"
                }
                articulos_lista.append(info_articulo)
        elif response.status_code == 429:
            print("Límite de peticiones alcanzado. Esperando...")
            time.sleep(10)
            continue
        else:
            print(f"Error {response.status_code}: {response.text}")
            break

        # NYT pide espaciar las llamadas a su API para evitar penalizaciones
        time.sleep(6)

df = pd.DataFrame(articulos_lista)

#pd.to_pickle(df, 'pickles/nyt.pkl')

# Mostrar los primeros resultados
print(f"\n¡Proceso completado! Se recolectaron {len(df)} artículos.")
print(df[["fecha", "titulo", "url"]].head())