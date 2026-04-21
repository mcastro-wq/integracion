import requests
import json

def descargar_via_api():
    datasets = {
        "detalle": "f9cc4ba0-931a-4b70-86c9-eacbd8c68596",
        "f12b": "c275fa9f-5c61-4313-828d-0827277bdd97",
        "situacion": "2c20b8e2-7bd9-41ba-8239-8f8c9571935a"
    }

    base_url = "https://api.datosabiertos.mef.gob.pe/DatosAbiertos/v1/datastore_search_sql?sql="

    for nombre, resource_id in datasets.items():
        try:
            print(f"Consultando {nombre}...")
            
            # SQL simplificado: Buscamos LAMBAYEQUE en cualquier columna de texto
            # Usamos un filtro más general por si ENTIDAD_NOMBRE no existe
            query = f'SELECT * FROM "{resource_id}" WHERE "SECTOR_NOMBRE" LIKE \'GOBIERNOS REGIONALES\' LIMIT 500'
            
            response = requests.get(base_url + query, timeout=60)
            data = response.json()

            records = []
            if data.get("success") and "result" in data:
                records = data["result"]["records"]
                # Filtramos Lambayeque manualmente por seguridad si la API no lo hizo bien
                records = [r for r in records if "LAMBAYEQUE" in str(r).upper()]
                print(f"Encontrados {len(records)} registros para {nombre}")

            # SEGURO: Si records está vacío o la API falló, guardamos un array vacío []
            # Esto evita el error de "file not found" en el siguiente paso
            with open(f"data_{nombre}.json", "w", encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"Fallo en {nombre}: {e}")
            # Creamos el archivo de emergencia
            with open(f"data_{nombre}.json", "w") as f:
                f.write("[]")

if __name__ == "__main__":
    descargar_via_api()
