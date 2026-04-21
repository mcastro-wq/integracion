import pandas as pd
import requests
import io
import sys

def descargar_y_recortar():
    datasets = {
        "detalle": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
        "situacion": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL.csv",
        "f12b": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B.csv"
    }

    cuis_lambayeque = []

    for nombre, url in datasets.items():
        try:
            print(f"Descargando {nombre}...")
            r = requests.get(url, timeout=300)
            sep_usar = ',' if nombre == 'f12b' else ';'
            
            # Cargamos el dataframe
            df = pd.read_csv(io.BytesIO(r.content), sep=sep_usar, encoding='latin-1', low_memory=False, on_bad_lines='skip')
            
            # Limpieza forzada de nombres de columnas
            df.columns = [str(c).strip().upper() for c in df.columns]

            if nombre == "detalle":
                # USAMOS POSICIÓN: 
                # Columna 0 es NIVEL
                # Columna 3 es CODIGO_UNICO
                # Filtramos donde la primera columna sea 'GR'
                df = df[df.iloc[:, 0].astype(str).str.contains('GR', na=False)].copy()
                
                # Extraemos los CUIs usando la posición 3
                cuis_lambayeque = df.iloc[:, 3].unique().tolist()
                print(f"Filtrado Nivel Regional: {len(df)} proyectos encontrados.")

            elif nombre in ["situacion", "f12b"]:
                # Filtramos usando la posición de CODIGO_UNICO (generalmente la 0 en estos archivos)
                col_cui = [c for c in df.columns if 'UNICO' in c or 'UNIC' in c]
                if col_cui:
                    df = df[df[col_cui[0]].isin(cuis_lambayeque)].copy()

            # Guardar JSON
            df.to_json(f"data_{nombre}.json", orient='records', force_ascii=False)
            print(f"Éxito: data_{nombre}.json generado.")

        except Exception as e:
            print(f"Error crítico en {nombre}: {e}")
            continue

if __name__ == "__main__":
    descargar_y_recortar()
