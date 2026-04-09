import pandas as pd
import requests
import json
import os

def descargar_data_abierta():
    # URLS de los Datasets de la plataforma de Datos Abiertos
    # Debes obtener los links directos (terminados en .csv) del portal
    urls = {
        "invierte": "URL_DATASET_INVIERTE_CSV",
        "presupuesto": "URL_DATASET_SNPP_CSV",
        "ceplan": "URL_DATASET_CEPLAN_CSV"
    }
    
    cui_objetivo = "2199528" # El CUI que estamos siguiendo
    data_final = {"cui": cui_objetivo}

    try:
        # 1. CRUCE CON INVIERTE.PE (SNA)
        # df_inv = pd.read_csv(urls["invierte"])
        # fila = df_inv[df_inv['CUI'] == int(cui_objetivo)]
        # Simulación de extracción:
        data_final["nombre"] = "MEJORAMIENTO DEL SERVICIO DE SEGURIDAD CIUDADANA EN CHICLAYO"
        data_final["monto_actualizado"] = 14388203.66
        
        # 2. CRUCE CON SNPP (Presupuesto)
        data_final["pim"] = 14388203.00
        data_final["devengado"] = 5420100.00
        
        # 3. CRUCE CON CEPLAN (Brechas)
        data_final["objetivo_estrategico"] = "Reducir el índice de victimización en la zona urbana"
        data_final["brecha"] = "Porcentaje de la población que no accede a servicios de videovigilancia"

        # Guardar el cruce en un JSON
        with open('data_cruzada.json', 'w', encoding='utf-8') as f:
            json.dump([data_final], f, indent=4, ensure_ascii=False)
            
        print("Cruce de bases de datos completado con éxito.")

    except Exception as e:
        print(f"Error en el cruce de datos: {e}")

if __name__ == "__main__":
    descargar_data_abierta()
