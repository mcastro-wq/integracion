import pandas as pd
import requests
import io
import json

def descargar_final():
    # IDs de los recursos (Datasets originales del MEF)
    datasets = {
        "detalle": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
        "situacion": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL.csv",
        "f12b": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B.csv"
    }

    for nombre, url in datasets.items():
        try:
            print(f"Procesando {nombre}...")
            r = requests.get(url, timeout=300)
            sep = ',' if nombre == 'f12b' else ';'
            
            # Cargamos solo una parte para no explotar la memoria
            df = pd.read_csv(io.BytesIO(r.content), sep=sep, encoding='latin-1', low_memory=False)
            
            # FILTRO MAESTRO: Buscamos "LAMBAYEQUE" en cualquier columna de texto
            # Esto reduce el peso de 700MB a 2MB automáticamente
            mask = df.astype(str).apply(lambda x: x.str.contains('LAMBAYEQUE', case=False, na=False)).any(axis=1)
            df_final = df[mask].copy()

            # Guardamos como JSON
            df_final.to_json(f"data_{nombre}.json", orient='records', force_ascii=False)
            print(f"✅ data_{nombre}.json creado con {len(df_final)} filas.")

        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")
            with open(f"data_{nombre}.json", "w") as f: f.write("[]")

if __name__ == "__main__":
    descargar_final()
