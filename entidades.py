# Seleccionar la entidad con a que se graficará la nube de palabras
# Opciones: 'PER', 'ORG', 'LOC', 'TODAS'
# 'PER': personas, 'ORG': organizaciones, 'LOC': lugares
# 'TODAS' es valor por defecto

# Seleccionar modelo: 'sm', 'md', 'lg'
# (sm: small, md: medium, lg: large)

# Correcciones 1: Incluir los términos que se quieren unificar o modificar
MAPEO_ENTIDADES = {
    "internet": "Internet",
    "Zuckerberg" : "Mark Zuckerberg"
}

# Correcciones 2: Lista de entidades basura para ignorar por completo
                     }

##########   FINAL DE LA CONFIGURACIÓN ############


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 300)
pd.set_option('display.max_colwidth', 40)

base = pd.read_pickle("pickles/base.pkl")

    nlp = spacy.load("es_core_news_" + modelo)

contador_categorias = Counter()
contador_entidades_exactas = Counter()

def extraer_entidades_y_contar(titulos_series):
    lista_entidades = []
    for doc in nlp.pipe(titulos_series, batch_size=50):
        entidades_doc = {}
        for ent in doc.ents:
            texto_limpio = ent.text.strip()
            texto_minuscula = texto_limpio.lower()
            if texto_minuscula in ENTIDADES_IGNORAR:
                continue
            if len(texto_limpio) <= 2:
                continue
            if texto_limpio.startswith("¿") or texto_limpio.startswith("?"):
                texto_limpio = texto_limpio.lstrip("¿?").strip()
                texto_minuscula = texto_limpio.lower()
            texto_unificado = MAPEO_ENTIDADES.get(texto_minuscula, texto_limpio)
            if ent.label_ not in entidades_doc:
                entidades_doc[ent.label_] = []
            if texto_unificado not in entidades_doc[ent.label_]:
                entidades_doc[ent.label_].append(texto_unificado)
            contador_categorias[ent.label_] += 1
            contador_entidades_exactas[(texto_unificado, ent.label_)] += 1
        lista_entidades.append(entidades_doc)
    return lista_entidades

base["entidades_raw"] = extraer_entidades_y_contar(base["titulo"])
base["Personas (PER)"] = base["entidades_raw"].apply(lambda x: x.get("PER", []))
base["Organizaciones (ORG)"] = base["entidades_raw"].apply(lambda x: x.get("ORG", []))
base["Lugares (LOC)"] = base["entidades_raw"].apply(lambda x: x.get("LOC", []))
base["Miscelánea (MISC)"] = base["entidades_raw"].apply(lambda x: x.get("MISC", []))
base = base.drop(columns=["entidades_raw"])

print("=" * 60)
print(" REPORTE GLOBAL DE ENTIDADES DETECTADAS")
print("=" * 60)

print(f"\nTotal de entidades encontradas: {sum(contador_categorias.values())}")
print("-" * 60)

print("\n1. Distribución por Categorías:")
for categoria, total in contador_categorias.items():
    print(f"   - {categoria:<5}: {total} detectadas")

print("\n2. Las 15 entidades más frecuentes en los títulos:")
print(f"   {'Entidad':<30} | {'Tipo':<6} | Frecuencia")
print("   " + "-" * 50)
for (texto, tipo), total in contador_entidades_exactas.most_common(15):
    print(f"   - {texto:<28} | {tipo:<6} | {total} veces")

print("\n" + "=" * 60)
print("Vista previa del DataFrame resultante:")
print("=" * 60)
print(
    base[
        [
            "Personas (PER)",
            "Organizaciones (ORG)",
            "Lugares (LOC)",
            "Miscelánea (MISC)",
        ]
    ]
)

if entidad_para_nube in ['PER', 'ORG', 'LOC']:
    frecuencias_nube = {
        texto: freq
        for (texto, tipo), freq in contador_entidades_exactas.items()
    }
else:
    frecuencias_nube = {
        texto: freq
        for (texto, tipo), freq in contador_entidades_exactas.items()
    }

wordcloud = WordCloud(
    width=1000,
    height=600,
    background_color="white",
    colormap="viridis",  # Opciones: 'plasma', 'inferno', 'coolwarm', etc.
    max_words=100,       # Límite de entidades a mostrar en la nube
).generate_from_frequencies(frecuencias_nube)

plt.figure(figsize=(12, 7))
plt.imshow(wordcloud, interpolation="bilinear")
plt.title("Entidades más frecuentes (" + entidad_para_nube +")")
plt.axis("off")

plt.show()
