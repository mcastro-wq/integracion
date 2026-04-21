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
            print(f"Procesando {nombre}...")
            r = requests.get(url, timeout=240)
            
            # Para el 12B usamos coma, para el resto punto y coma (según estándar MEF)
            sep_usar = ',' if nombre == 'f12b' else ';'
            
            # Cargamos con 'on_bad_lines' para saltar filas corruptas que dan el error de tokenizing
            df = pd.read_csv(
                io.BytesIO(r.content), 
                sep=sep_usar, 
                encoding='latin-1', 
                low_memory=False,
                on_bad_lines='skip',
                quotechar='"'
            )
            
            # Limpieza de cabeceras
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # FILTRADO:
            # Si es el archivo 'detalle', filtramos por Lambayeque para reducir peso
            if nombre == "detalle":
                df = df[df['DEPARTAMENTO'].astype(str).str.contains('LAMBAYEQUE', na=False)]
            
            # Si son los otros dos, los filtramos cruzándolos con los CUIs que quedaron en 'detalle'
            # Esto hace que data_situacion y data_f12b sean archivos pequeñitos solo de Lambayeque
            if nombre == "detalle":
                lista_cuis = df['CODIGO_UNICO'].unique().tolist()
                self_cuis = lista_cuis # Guardamos para los siguientes ciclos
            
            if nombre in ["situacion", "f12b"] and 'self_cuis' in locals():
                df = df[df['CODIGO_UNICO'].isin(self_cuis)]

            # Guardar JSON
            df.to_json(f"data_{nombre}.json", orient='records', force_ascii=False, indent=2)
            print(f"Éxito: data_{nombre}.json generado con {len(df)} registros.")

        except Exception as e:
            print(f"Error crítico en {nombre}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    descargar_y_filtrar()
