import requests
import json

# Solo el ID de Detalle que es el más pesado
RECURSO_DETALLE = "f9cc4ba0-931a-4b70-86c9-eacbd8c68596"

def descargar_por_partes():
    limit = 10000
    for i in range(3): # Descargará 3 partes (30,000 registros en total)
        offset = i * limit
        print(f"Descargando parte {i+1} (Inicio: {offset})...")
        url = f"https://api.datosabiertos.mef.gob.pe/DatosAbiertos/v1/datastore_search?resource_id={RECURSO_DETALLE}&limit={limit}&offset={offset}"
        
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                records = r.json()["result"]["records"]
                with open(f"data_parte_{i+1}.json", "w", encoding='utf-8') as f:
                    json.dump(records, f, ensure_ascii=False)
                print(f"✅ Parte {i+1} guardada.")
            else:
                print(f"❌ Error en parte {i+1}")
        except Exception as e:
            print(f"❌ Fallo crítico: {e}")

if __name__ == "__main__":
    descargar_por_partes()
