import pandas as pd
import requests
import json
import io

def extraer_todo_invierte():
    url_invierte = "https://ofi5.mef.gob.pe/invierteWS/Ssi/expRepSSIDet"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json;charset=UTF-8"
    }

    payload = {
        "nivel": "R", 
        "region": "14", 
        "tipo": "0" 
    }

    try:
        print("Accediendo a Invierte.pe...")
        response = requests.post(url_invierte, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            # Leer Excel
            df = pd.read_excel(io.BytesIO(response.content))
            
            # Limpiar nombres de columnas (quitar espacios locos)
            df.columns = df.columns.str.strip()
            
            # Seleccionamos y renombramos según tus cabeceras exactas
            # Nota: Usamos DEVENGADO ACUMULADO para el gasto total histórico
            df_final = df[[
                'CUI', 
                'NOMBRE DE LA INVERSION', 
                'COSTO ACTUALIZADO', 
                'PIM 2023', # Cambiar a 2026 si el sistema ya lo reporta así
                'DEVENGADO 2023', 
                'DEVENGADO ACUMULADO',
                'ESTADO',
                'SITUACION'
            ]].rename(columns={
                'CUI': 'cui',
                'NOMBRE DE LA INVERSION': 'nombre',
                'COSTO ACTUALIZADO': 'monto_actualizado',
                'PIM 2023': 'pim',
                'DEVENGADO 2023': 'devengado_anual',
                'DEVENGADO ACUMULADO': 'devengado'
            })

            # Convertir CUI a string para evitar problemas de búsqueda en JS
            df_final['cui'] = df_final['cui'].astype(str)
            df_final = df_final.fillna(0)

            # Guardar JSON
            lista_proyectos = df_final.to_dict(orient='records')
            with open('data_cruzada.json', 'w', encoding='utf-8') as f:
                json.dump(lista_proyectos, f, indent=4, ensure_ascii=False)
            
            print(f"¡Cruce exitoso! {len(lista_proyectos)} proyectos procesados.")
        else:
            print(f"Error en servidor MEF: {response.status_code}")

    except Exception as e:
        print(f"Error procesando el Excel: {e}")

if __name__ == "__main__":
    extraer_todo_invierte()
