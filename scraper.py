import requests
import pandas as pd
import json
import io
import os

# Los 3 enlaces directos a los CSV del MEF
ENLACES = {
    "detalle": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
    "f12b": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B_INVERSIONES.csv",
    "situacion": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL_INVERSIONES.csv"
}

def procesar_mef():
    for nombre, url in ENLACES.items():
        print(f"Descargando {nombre}...")
        try:
            r = requests.get(url, timeout=150)
            if r.status_code == 200:
                # Leemos CSV con pandas detectando el separador automáticamente (suelen ser ;)
                df = pd.read_csv(io.BytesIO(r.content), sep=None, engine='python', encoding='utf-8-sig')
                
                # Dividimos en bloques de 10,000 para mantener archivos ligeros
                chunk_size = 10000
                partes = (len(df) // chunk_size) + 1
                
                for i in range(partes):
                    chunk = df.iloc[i*chunk_size : (i+1)*chunk_size]
                    if not chunk.empty:
                        # Ejemplo: data_f12b_parte_1.json
                        chunk.to_json(f"data_{nombre}_parte_{i+1}.json", orient='records', force_ascii=False)
                print(f"✅ {nombre} procesado en {partes} partes.")
        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")

if __name__ == "__main__":
    procesar_mef()
