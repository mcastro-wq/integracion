import requests
import json

def ejecutar_consulta():
    # IDs de recursos que me pasaste
    datasets = {
        "detalle": "f9cc4ba0-931a-4b70-86c9-eacbd8c68596",
        "f12b": "c275fa9f-5c61-4313-828d-0827277bdd97",
        "situacion": "2c20b8e2-7bd9-41ba-8239-8f8c9571935a"
    }

    base_url = "https://api.datosabiertos.mef.gob.pe/DatosAbiertos/v1/datastore_search_sql?sql="

    for nombre, res_id in datasets.items():
        try:
            print(f"Consultando {nombre}...")
            # SQL: Seleccionamos todo donde la entidad contenga 'LAMBAYEQUE'
            # Esto garantiza que el archivo JSON sea pequeño y contenga datos reales
            query = f'SELECT * FROM "{res_id}" WHERE "ENTIDAD_NOMBRE" LIKE \'%LAMBAYEQUE%\''
            
            r = requests.get(base_url + query, timeout=60)
            data = r.json()

            if data.get("success"):
                records = data["result"]["records"]
                with open(f"data_{nombre}.json", "w", encoding='utf-8') as f:
                    json.dump(records, f, ensure_ascii=False, indent=2)
                print(f"✅ {nombre}: {len(records)} proyectos guardados.")
            else:
                # Si falla la columna ENTIDAD_NOMBRE, intentamos una búsqueda general sin filtro para no romper el proceso
                print(f"⚠️ Filtro SQL falló en {nombre}, reintentando búsqueda general...")
                query_alt = f'SELECT * FROM "{res_id}" LIMIT 1000'
                r_alt = requests.get(base_url + query_alt)
                records = r_alt.json()["result"]["records"]
                # Filtramos en Python por si acaso
                records = [reg for reg in records if "LAMBAYEQUE" in str(reg).upper()]
                with open(f"data_{nombre}.json", "w", encoding='utf-8') as f:
                    json.dump(records, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")
            with open(f"data_{nombre}.json", "w") as f: f.write("[]")

if __name__ == "__main__":
    ejecutar_consulta()
