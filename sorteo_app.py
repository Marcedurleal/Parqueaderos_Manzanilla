import streamlit as st
import pandas as pd
import random
import time
import io

st.set_page_config(page_title="Sorteo de Parqueaderos", page_icon="🚗", layout="wide")

st.title("🚗 Sistema Digital de Sorteo de Parqueaderos")
st.markdown("""
Esta aplicación automatiza la asignación aleatoria de parqueaderos. 
**Nueva Lógica:** Al haber más apartamentos que parqueaderos, el sistema seleccionará aleatoriamente quiénes obtienen parqueadero y quiénes quedan en lista de espera.
""")

# Sección de Carga de Archivos
st.sidebar.header("📁 Carga de Datos")
uploaded_file = st.sidebar.file_uploader("Carga tu archivo Excel (.xlsx)", type=["xlsx"])

# Datos de ejemplo para simulación
def cargar_datos_ejemplo():
    parqueaderos = [f"P-{i:03d}" for i in range(1, 16)] # 15 parqueaderos
    apartamentos = [f"Torre {t} - Apt {a:03d}" for t in range(1, 4) for a in range(101, 109)] # 24 apartamentos
    df_pq = pd.DataFrame({"Parqueadero": parqueaderos})
    df_ap = pd.DataFrame({"Apartamento": apartamentos})
    return df_pq, df_ap

if not uploaded_file:
    st.info("💡 Por favor, carga un archivo Excel en la barra lateral o usa los datos de simulación para probar el sistema.")
    if st.checkbox("Usar datos de simulación/ejemplo con más apartamentos que parqueaderos"):
        df_pq, df_ap = cargar_datos_ejemplo()
        st.success("¡Datos de simulación cargados!")
    else:
        st.stop()
else:
    try:
        xl = pd.ExcelFile(uploaded_file)
        hojas = xl.sheet_names
        
        st.sidebar.subheader("Configuración de Hojas")
        hoja_pq = st.sidebar.selectbox("Hoja de Parqueaderos", hojas, index=0 if "parqueaderos" in [h.lower() for h in hojas] else 0)
        hoja_ap = st.sidebar.selectbox("Hoja de Apartamentos", hojas, index=1 if "apartamentos" in [h.lower() for h in hojas] else (1 if len(hojas)>1 else 0))
        
        df_pq = pd.read_excel(uploaded_file, sheet_name=hoja_pq)
        df_ap = pd.read_excel(uploaded_file, sheet_name=hoja_ap)
    except Exception as e:
        st.error(f"❌ Error al leer el archivo Excel: {e}")
        st.stop()

# Validación y preparación de datos
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Parqueaderos Disponibles")
    col_pq = st.selectbox("Columna de Parqueaderos", df_pq.columns)
    lista_parqueaderos = df_pq[col_pq].dropna().astype(str).tolist()
    st.write(f"Total parqueaderos: **{len(lista_parqueaderos)}**")
    st.dataframe(df_pq[[col_pq]], height=150, use_container_width=True)

with col2:
    st.subheader("🏢 Apartamentos Participantes")
    col_ap = st.selectbox("Columna de Apartamentos", df_ap.columns)
    lista_apartamentos = df_ap[col_ap].dropna().astype(str).tolist()
    st.write(f"Total apartamentos: **{len(lista_apartamentos)}**")
    st.dataframe(df_ap[[col_ap]], height=150, use_container_width=True)

if len(lista_parqueaderos) == 0 or len(lista_apartamentos) == 0:
    st.warning("⚠️ Asegúrate de que ambas listas tengan datos válidos.")
    st.stop()

# Informar la situación del sorteo
st.markdown("---")
st.subheader("⚙️ Configuración del Sorteo Visual")

if len(lista_apartamentos) > len(lista_parqueaderos):
    dif = len(lista_apartamentos) - len(lista_parqueaderos)
    st.warning(f"📢 **Nota del Sorteo:** Hay más apartamentos ({len(lista_apartamentos)}) que parqueaderos ({len(lista_parqueaderos)}). Al finalizar, **{dif}** apartamentos quedarán en lista de espera.")
else:
    st.info("Nota: Hay suficientes parqueaderos para todos los apartamentos.")

velocidad = st.slider("Velocidad de la animación (segundos por asignación)", min_value=0.05, max_value=1.5, value=0.3, step=0.05)

# Inicializar estados de la sesión
if "sorteo_realizado" not in st.session_state:
    st.session_state.sorteo_realizado = False
if "resultados_df" not in st.session_state:
    st.session_state.resultados_df = None

# Botón Principal
if st.button("🚀 INICIAR SORTEO PÚBLICO", type="primary"):
    st.session_state.sorteo_realizado = False
    
    # 1. Mezclar completamente la lista de apartamentos para asegurar aleatoriedad total
    ap_mezclados = lista_apartamentos.copy()
    random.shuffle(ap_mezclados)
    
    # 2. Mezclar los parqueaderos disponibles
    pq_disponibles = lista_parqueaderos.copy()
    random.shuffle(pq_disponibles)
    
    # 3. Separar los apartamentos que alcanzan parqueadero y los que van a lista de espera
    cant_parqueaderos = len(pq_disponibles)
    ap_con_parqueadero = ap_mezclados[:cant_parqueaderos]
    ap_sin_parqueadero = ap_mezclados[cant_parqueaderos:]
    
    # Contenedores para la animación
    st.subheader("🔮 Proceso de Asignación en Tiempo Real")
    progreso_bar = st.progress(0)
    status_text = st.empty()
    pantalla_animacion = st.empty()
    tabla_en_vivo = st.empty()
    
    resultados_lista = []
    total_sorteos = len(ap_con_parqueadero)
    
    # 4. Sorteo Visual (Solo para los que ganaron parqueadero)
    for i, apto in enumerate(ap_con_parqueadero):
        pq_asignado = pq_disponibles[i]
        
        # Animación de ruleta
        for _ in range(6):
            opcion_aleatoria = random.choice(pq_disponibles[i:])
            pantalla_animacion.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; border: 2px dashed #31333F;">
                <h3 style="margin: 0; color: #555;">Buscando parqueadero para: <b>{apto}</b></h3>
                <h1 style="margin: 10px 0; color: #ff4b4b; font-size: 40px;">🔄 {opcion_aleatoria}</h1>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.04)
            
        # Guardar resultado real
        resultados_lista.append({"Apartamento": apto, "Parqueadero Asignado": pq_asignado})
        
        # Mostrar resultado fijo en pantalla
        pantalla_animacion.markdown(f"""
        <div style="background-color: #d4edda; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #28a745;">
            <h3 style="margin: 0; color: #155724;">¡ASIGNADO!</h3>
            <h2 style="margin: 5px 0; color: #155724;">🏢 {apto}</h2>
            <h1 style="margin: 5px 0; color: #28a745; font-size: 45px;">🚗 {pq_asignado}</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso en la pantalla
        porcentaje = int((i + 1) / total_sorteos * 100)
        progreso_bar.progress(porcentaje)
        status_text.markdown(f"Asignados de forma visible: **{i+1}** de **{total_sorteos}** parqueaderos.")
        
        # Mostrar los últimos resultados en una tabla pequeña
        df_actual = pd.DataFrame(resultados_lista)
        tabla_en_vivo.dataframe(df_actual.tail(5), use_container_width=True)
        
        time.sleep(velocidad)
        
    # 5. Agregar automáticamente los apartamentos que se quedaron sin parqueadero al reporte
    for apto in ap_sin_parqueadero:
        resultados_lista.append({"Apartamento": apto, "Parqueadero Asignado": "Sin Parqueadero Asignado (Lista de espera)"})
        
    pantalla_animacion.empty()
    st.balloons()
    st.success("🎉 ¡El sorteo ha finalizado! Se han asignado todos los estacionamientos disponibles.")
    
    # Guardar en el estado de Streamlit
    st.session_state.resultados_df = pd.DataFrame(resultados_lista)
    st.session_state.sorteo_realizado = True

# Mostrar Resultados Finales y Descarga de Excel
if st.session_state.sorteo_realizado and st.session_state.resultados_df is not None:
    st.markdown("---")
    st.subheader("🏆 Resultados Oficiales del Sorteo")
    
    res_df = st.session_state.resultados_df
    
    # Buscador interactivo para los copropietarios
    buscar_apto = st.text_input("🔍 Buscar mi apartamento (ej: Torre 1):")
    if buscar_apto:
        df_filtrado = res_df[res_df['Apartamento'].str.contains(buscar_apto, case=False, na=False)]
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.dataframe(res_df, use_container_width=True)
        
    # Generar el archivo Excel descargable con openpyxl
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        res_df.to_excel(writer, index=False, sheet_name='Resultados_Sorteo')
    processed_data = output.getvalue()
    
    st.download_button(
        label="📥 Descargar Acta de Resultados en Excel",
        data=processed_data,
        file_name="acta_sorteo_parqueaderos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
