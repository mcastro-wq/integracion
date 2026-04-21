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
            
            df = pd.read_csv(io.BytesIO(r.content), sep=sep_usar, encoding='latin-1', low_memory=False, on_bad_lines='skip')
            df.columns = [str(c).strip().upper() for c in df.columns]

            if nombre == "detalle":
                # APLICANDO TU FILTRO ESPECÍFICO
                # 1. Nivel debe ser GR
                # 2. Entidad debe contener LAMBA
                df = df[
                    (df['NIVEL'] == 'GR') & 
                    (df['ENTIDAD'].astype(str).str.contains('LAMBA', na=False))
                ].copy()
                
                cuis_lambayeque = df['CODIGO_UNICO'].unique().tolist()
                print(f"Filtrado Sede Central Lambayeque: {len(df)} proyectos encontrados.")

            elif nombre in ["situacion", "f12b"]:
                # Filtramos Situación y 12B por los CUIs resultantes para mantener coherencia
                if cuis_lambayeque:
                    df = df[df['CODIGO_UNICO'].isin(cuis_lambayeque)].copy()

            # Guardar JSON
            df.to_json(f"data_{nombre}.json", orient='records', force_ascii=False)
            print(f"Éxito: data_{nombre}.json generado.")

        except Exception as e:
            print(f"Error en {nombre}: {e}")
            continue

if __name__ == "__main__":
    descargar_y_recortar()
