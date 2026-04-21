import requests
import pandas as pd
import json
import io

# Enlaces directos a los CSV del MEF
ENLACES = {
    "detalle": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
    "f12b": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B_INVERSIONES.csv",
    "situacion": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL_INVERSIONES.csv"
}

def procesar_mef():
    # Configuramos una sesión para manejar mejor las cookies y redirecciones
    session = requests.Session()
    session.max_redirects = 60 # Aumentamos el límite para evitar el error de tu captura
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    for nombre, url in ENLACES.items():
        print(f"Descargando {nombre}...")
        try:
            # allow_redirects=True es vital aquí
            r = session.get(url, timeout=180, allow_redirects=True)
            
            if r.status_code == 200:
                # El separador en estos archivos suele ser punto y coma (;)
                df = pd.read_csv(io.BytesIO(r.content), sep=None, engine='python', encoding='utf-8-sig')
                
                # Fragmentamos en 10,000 filas por parte
                chunk_size = 10000
                total_filas = len(df)
                partes = (total_filas // chunk_size) + 1
                
                for i in range(partes):
                    chunk = df.iloc[i*chunk_size : (i+1)*chunk_size]
                    if not chunk.empty:
                        chunk.to_json(f"data_{nombre}_parte_{i+1}.json", orient='records', force_ascii=False)
                print(f"✅ {nombre} procesado con éxito.")
            else:
                print(f"❌ Error {r.status_code} al descargar {nombre}")
        except Exception as e:
            print(f"❌ Error crítico en {nombre}: {e}")

if __name__ == "__main__":
    procesar_mef()
