import pandas as pd
import requests
import io

def descargar_y_recortar():
    datasets = {
        "detalle": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
        "situacion": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL.csv",
        "f12b": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B.csv"
    }

    cuis_gr = []

    for nombre, url in datasets.items():
        try:
            print(f"Descargando {nombre}...")
            r = requests.get(url, timeout=300)
            sep_usar = ',' if nombre == 'f12b' else ';'
            
            df = pd.read_csv(io.BytesIO(r.content), sep=sep_usar, encoding='latin-1', low_memory=False, on_bad_lines='skip')
            
            if nombre == "detalle":
                # Filtramos la primera columna (Nivel) que sea GR
                df = df[df.iloc[:, 0].astype(str).str.contains('GR', na=False)].copy()
                cuis_gr = df.iloc[:, 3].unique().tolist() # Columna 3 es CODIGO_UNICO
                print(f"Proyectos GR encontrados: {len(df)}")

            elif nombre in ["situacion", "f12b"]:
                # Intentamos filtrar por CUI si tenemos la lista
                col_cui = [c for c in df.columns if 'UNICO' in str(c).upper()]
                if col_cui and cuis_gr:
                    df = df[df[col_cui[0]].isin(cuis_gr)].copy()

            # GUARDAR SIEMPRE: Aunque esté vacío, generamos el archivo para que Git no falle
            df.to_json(f"data_{nombre}.json", orient='records', force_ascii=False)
            print(f"Archivo data_{nombre}.json generado correctamente.")

        except Exception as e:
            print(f"Error en {nombre}: {e}")
            # Si falla, creamos un archivo vacío de emergencia
            with open(f"data_{nombre}.json", "w") as f:
                f.write("[]")

if __name__ == "__main__":
    descargar_y_recortar()
