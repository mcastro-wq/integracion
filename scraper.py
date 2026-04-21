import pandas as pd
import requests
import io

def descargar_y_recortar():
    # Eliminamos "detalle" de la lista para evitar el archivo pesado
    datasets = {
        "detalle": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
        "situacion": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL.csv",
        "f12b": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B.csv"
    }

    for nombre, url in datasets.items():
        try:
            print(f"Descargando {nombre}...")
            r = requests.get(url, timeout=300)
            
            # El Formato 12B suele usar coma, Estado Situacional punto y coma
            sep_usar = ',' if nombre == 'f12b' else ';'
            
            df = pd.read_csv(io.BytesIO(r.content), sep=sep_usar, encoding='latin-1', low_memory=False, on_bad_lines='skip')
            
            # Guardamos el JSON completo (Situación y 12B por sí solos suelen pesar menos de 100MB)
            df.to_json(f"data_{nombre}.json", orient='records', force_ascii=False)
            print(f"Archivo data_{nombre}.json generado correctamente.")

        except Exception as e:
            print(f"Error en {nombre}: {e}")
            # Archivo vacío de emergencia para que el .yml no falle
            with open(f"data_{nombre}.json", "w") as f:
                f.write("[]")

if __name__ == "__main__":
    descargar_y_recortar()
