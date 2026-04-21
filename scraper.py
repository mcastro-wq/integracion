import requests
import pandas as pd
import json
import io

# Enlaces directos a los CSV (sustituyendo la API SQL que falla)
ENLACES = {
    "detalle": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
    "f12b": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B_INVERSIONES.csv",
    "situacion": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL_INVERSIONES.csv"
}

def procesar_archivos():
    for nombre, url in ENLACES.items():
        print(f"Descargando CSV de {nombre}...")
        try:
            # Descarga el archivo completo
            response = requests.get(url, timeout=120)
            if response.status_code == 200:
                # Usamos pandas para leer el CSV (el MEF suele usar separador ';')
                df = pd.read_csv(io.BytesIO(response.content), sep=None, engine='python', encoding='utf-8-sig')
                
                # Dividir en partes de 10,000 registros para que el JSON no sea gigante
                chunk_size = 10000
                total_filas = len(df)
                partes = (total_filas // chunk_size) + 1
                
                for i in range(partes):
                    inicio = i * chunk_size
                    fin = inicio + chunk_size
                    chunk = df.iloc[inicio:fin]
                    
                    if not chunk.empty:
                        archivo_nombre = f"data_{nombre}_parte_{i+1}.json"
                        chunk.to_json(archivo_nombre, orient='records', force_ascii=False)
                        print(f"✅ Generado: {archivo_nombre}")
            else:
                print(f"❌ No se pudo descargar {nombre}. Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error procesando {nombre}: {e}")

if __name__ == "__main__":
    procesar_archivos()
