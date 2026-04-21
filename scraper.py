import requests
import json

def descargar_via_api():
    # Diccionario con los IDs de los recursos y el nombre del archivo final
    datasets = {
        "detalle": "f9cc4ba0-931a-4b70-86c9-eacbd8c68596",
        "f12b": "c275fa9f-5c61-4313-828d-0827277bdd97",
        "situacion": "2c20b8e2-7bd9-41ba-8239-8f8c9571935a"
    }

    base_url = "https://api.datosabiertos.mef.gob.pe/DatosAbiertos/v1/datastore_search_sql?sql="

    for nombre, resource_id in datasets.items():
        try:
            print(f"Consultando API para {nombre}...")
            
            # SQL: Seleccionamos todo donde el sector sea GOBIERNOS REGIONALES 
            # Y la entidad contenga LAMBAYEQUE
            query = f'SELECT * FROM "{resource_id}" WHERE "SECTOR_NOMBRE" LIKE \'GOBIERNOS REGIONALES\' AND "ENTIDAD_NOMBRE" LIKE \'%LAMBAYEQUE%\''
            
            response = requests.get(base_url + query, timeout=60)
            data = response.json()

            # La API devuelve los datos dentro de success -> result -> records
            if data.get("success"):
                records = data["result"]["records"]
                
                with open(f"data_{nombre}.json", "w", encoding='utf-8') as f:
                    json.dump(records, f, ensure_ascii=False, indent=2)
                
                print(f"Éxito: data_{nombre}.json generado con {len(records)} registros.")
            else:
                print(f"Error en API para {nombre}: {data.get('error')}")

        except Exception as e:
            print(f"Fallo en {nombre}: {e}")

if __name__ == "__main__":
    descargar_via_api()
