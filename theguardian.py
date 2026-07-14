import requests
import pandas as pd
import time
import re

# Configuración inicial
API_KEY = ""  # Colocar la clave generada
URL_BASE = "https://content.guardianapis.com/search"

# Parámetros de búsqueda
filtro_busqueda = '"artificial intelligence" AND (work OR job)'

articulos_lista = []

#anios = ["2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
anios = ["2025", "2026"]

for anio in anios:
    print(f"--- Descargando año {anio} ---")

    fecha_inicio = f"{anio}-01-01"
    fecha_fin = f"{anio}-12-31" if anio != 2026 else "2026-06-01"

    for page in range(1, 5):
        print(f"Descargando página {page}...")

        params = {
            "q": filtro_busqueda,
            "from-date": fecha_inicio,
            "to-date": fecha_fin,
            "page": page,
            "page-size": 10,
            "order-by": "oldest",
            "show-fields": "bodyText,trailText",
            "api-key": API_KEY
        }

        response = requests.get(URL_BASE, params=params)

        if response.status_code == 200:
            data = response.json()
            results = data.get("response", {}).get("results", [])
            for doc in results:
                fields = doc.get("fields", {})
                copete_raw = fields.get("trailText", "")
                copete_limpio = re.sub('<[^<]+?>', '', copete_raw) if copete_raw else ""
                info_articulo = {
                    "anio_busqueda": anio,
                    "fecha": doc.get("webPublicationDate"),
                    "titulo": doc.get("webTitle"),
                    "texto" : fields.get("bodyText"),
                    "copete": copete_limpio,
                    "url": doc.get("webUrl"),
                    "medio" : "theguardian"
                }
                articulos_lista.append(info_articulo)
        elif response.status_code == 429:
            print("Límite de peticiones alcanzado. Esperando...")
            time.sleep(10)
            continue
        else:
            print(f"Error {response.status_code}: {response.text}")
            break

        time.sleep(6)

df = pd.DataFrame(articulos_lista)

print(f"\n¡Proceso completado! Se recolectaron {len(df)} artículos.")
print(f"Total de artículos recolectados: {len(df)}")

if not df.empty:
    print("\nDistribución de artículos recolectados por año:")
    print(df["anio_busqueda"].value_counts().sort_index())

df = df.drop('anio_busqueda', axis=1)
#pd.to_pickle(df, 'pickles/theguardian.pkl')
