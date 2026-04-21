import pandas as pd
import requests
import json
import io
import sys

def descargar_y_filtrar():
    datasets = {
        "detalle": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
        "situacion": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL.csv",
        "f12b": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B.csv"
    }

    for nombre, url in datasets.items():
        try:
            print(f"Descargando {nombre}...")
            r = requests.get(url, timeout=180)
            df = pd.read_csv(io.BytesIO(r.content), sep=';', encoding='latin-1', low_memory=False)
            
            # Limpiar columnas
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Filtrar solo Lambayeque para que los JSON no pesen demasiado
            # Buscamos cualquier columna que diga DEPARTAMENTO
            col_dep = [c for c in df.columns if 'DEPARTAMENTO' in c]
            if col_dep:
                df = df[df[col_dep[0]].astype(str).str.contains('LAMBAYEQUE', na=False)]
            
            # Guardar como JSON individual
            archivo_final = f"data_{nombre}.json"
            df.to_json(archivo_final, orient='records', force_ascii=False, indent=2)
            print(f"Guardado: {archivo_final}")

        except Exception as e:
            print(f"Error con {nombre}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    descargar_y_filtrar()
