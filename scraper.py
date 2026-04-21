import pandas as pd
import requests
import json
import io
import sys

def integrar_data_maestra():
    # Enlaces de Datos Abiertos
    urls = {
        "detalle": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
        "situacion": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL.csv",
        "et": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/INVERSIONES_ET.csv",
        "f12b": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B.csv"
    }
    
    print("Iniciando descarga masiva e integración de datos...")

    try:
        # 1. Cargar Detalle Principal (Maestro)
        res_det = requests.get(urls["detalle"], timeout=180)
        df_det = pd.read_csv(io.BytesIO(res_det.content), sep=';', encoding='latin-1', low_memory=False)
        df_det.columns = df_det.columns.str.strip().upper()
        # Filtro Lambayeque
        df_det = df_det[df_det['DEPARTAMENTO'] == 'LAMBAYEQUE'].copy()

        # 2. Cargar Estado Situacional (Problemáticas)
        res_sit = requests.get(urls["situacion"], timeout=120)
        df_sit = pd.read_csv(io.BytesIO(res_sit.content), sep=';', encoding='latin-1', low_memory=False)
        df_sit.columns = df_sit.columns.str.strip().upper()

        # 3. Cargar Datos de Expediente Técnico
        res_et = requests.get(urls["et"], timeout=120)
        df_et = pd.read_csv(io.BytesIO(res_et.content), sep=';', encoding='latin-1', low_memory=False)
        df_et.columns = df_et.columns.str.strip().upper()

        # 4. Cargar Formato 12B (Avance físico y comentarios)
        res_12b = requests.get(urls["f12b"], timeout=120)
        df_12b = pd.read_csv(io.BytesIO(res_12b.content), sep=';', encoding='latin-1', low_memory=False)
        df_12b.columns = df_12b.columns.str.strip().upper()

        maestro_final = []

        for _, row in df_det.iterrows():
            cui_val = row['CODIGO_UNIC']
            
            # --- CRUCE CON ESTADO SITUACIONAL ---
            sit_row = df_sit[df_sit['CODIGO_UNIC'] == cui_val].sort_values('FECHA_REGISTRO', ascending=False)
            comentario_situacional = sit_row.iloc[0]['DESCRIPCION'] if not sit_row.empty else "Sin reporte situacional reciente"

            # --- CRUCE CON EXPEDIENTE TÉCNICO ---
            et_row = df_et[df_et['CODIGO_UNIC'] == cui_val]
            tiene_et = "SÍ" if not et_row.empty else "NO"
            monto_et = float(et_row.iloc[0]['ULT_MTO_ET']) if not et_row.empty else 0

            # --- CRUCE CON 12B (SEGUIMIENTO) ---
            f12b_row = df_12b[df_12b['CODIGO_UNIC'] == cui_val]
            avance_fisico = float(f12b_row.iloc[0]['AVANCE_FISIC']) if not f12b_row.empty else row.get('AVANCE_FISICO', 0)
            proximos_pasos = f12b_row.iloc[0]['ACC_PROBLEMA'] if not f12b_row.empty else "Continuar ejecución"

            proyecto = {
                "cui": str(cui_val),
                "nombre": row.get('NOMBRE_INVERSION', 'N/A'),
                "costo_actualizado": float(row.get('COSTO_ACTUALIZADO', 0)),
                "pim_2026": float(row.get('PIM_ANIO_ACTUAL', 0)),
                "devengado_acumulado": float(row.get('DEVEN_ACUMUL_ANIO_ANT', 0)) + float(row.get('DEV_ANIO_ACTUAL', 0)),
                "avance_fisico_porc": avance_fisico,
                "estado_invierte": row.get('ESTADO', 'N/A'),
                "situacion_invierte": row.get('SITUACION', 'N/A'),
                "estado_situacional_mef": comentario_situacional,
                "tiene_expediente": tiene_et,
                "monto_expediente": monto_et,
                "seguimiento_proximos_pasos": proximos_pasos,
                "unidad_ejecutora": row.get('NOMBRE_UEP', 'N/A')
            }
            maestro_final.append(proyecto)

        # Guardar el JSON Integrado
        with open('data_cruzada.json', 'w', encoding='utf-8') as f:
            json.dump(maestro_final, f, indent=4, ensure_ascii=False)
        
        print(f"¡Integración Exitosa! {len(maestro_final)} proyectos de Lambayeque cruzados.")

    except Exception as e:
        print(f"Error en la integración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    integrar_data_maestra()
