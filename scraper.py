import requests
import json

# IDs de tus diccionarios
recursos = {
    "detalle": "f9cc4ba0-931a-4b70-86c9-eacbd8c68596",
    "f12b": "c275fa9f-5c61-4313-828d-0827277bdd97",
    "situacion": "2c20b8e2-7bd9-41ba-8239-8f8c9571935a"
}

def descargar_datos():
    for nombre, res_id in recursos.items():
        # Usamos la API pero con un límite alto para tener datos locales
        url = f"https://api.datosabiertos.mef.gob.pe/DatosAbiertos/v1/datastore_search?resource_id={res_id}&limit=5000"
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                datos = r.json()["result"]["records"]
                # Filtramos solo Lambayeque para no saturar tu GitHub
                filtrados = [reg for reg in datos if "LAMBAYEQUE" in str(reg).upper()]
                with open(f"data_{nombre}.json", "w", encoding='utf-8') as f:
                    json.dump(filtrados, f, ensure_ascii=False)
                print(f"✅ {nombre} actualizado.")
        except:
            print(f"❌ Falló {nombre}")

if __name__ == "__main__":
    descargar_datos()
