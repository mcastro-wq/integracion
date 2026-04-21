import pandas as pd
import requests
import io
import sys

def descargar_todo():
    datasets = {
        "detalle": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
        "situacion": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL.csv",
        "f12b": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B.csv"
    }

    for nombre, url in datasets.items():
        try:
            print(f"Descargando {nombre}...")
            r = requests.get(url, timeout=300)
            
            # El 12B usa coma, los otros punto y coma. 
            # 'on_bad_lines' evita que el script muera si el MEF subió algo mal.
            sep_usar = ',' if nombre == 'f12b' else ';'
            df = pd.read_csv(io.BytesIO(r.content), sep=sep_usar, encoding='latin-1', low_memory=False, on_bad_lines='skip')
            
            # Guardamos el JSON sin filtrar nada
            df.to_json(f"data_{nombre}.json", orient='records', force_ascii=False)
            print(f"Éxito: data_{nombre}.json generado.")

        except Exception as e:
            print(f"Error con {nombre}: {e}")
            continue # Si uno falla, sigue con el siguiente

if __name__ == "__main__":
    descargar_todo()
