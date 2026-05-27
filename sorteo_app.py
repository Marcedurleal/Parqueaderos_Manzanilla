
import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Sorteo de Parqueaderos", page_icon="🚗", layout="wide")

st.title("🚗 Sistema Digital de Sorteo de Parqueaderos")
st.markdown("""
Esta aplicación automatiza la asignación aleatoria y equitativa de parqueaderos a los apartamentos de un conjunto residencial. 
El proceso cuenta con una animación visible y transparente para asegurar la confianza de todos los copropietarios.
""")

# Sección de Carga de Archivos
st.sidebar.header("📁 Carga de Datos")
uploaded_file = st.sidebar.file_uploader("Carga tu archivo Excel (.xlsx)", type=["xlsx"])

# Datos de ejemplo por si el usuario no tiene un archivo a la mano
def cargar_datos_ejemplo():
    parqueaderos = [f"P-{i:03d}" for i in range(1, 31)]
    apartamentos = [f"Torre {t} - Apt {a:03d}" for t in range(1, 4) for a in range(101, 111)]
    df_pq = pd.DataFrame({"Parqueadero": parqueaderos})
    df_ap = pd.DataFrame({"Apartamento": apartamentos})
    return df_pq, df_ap

if not uploaded_file:
    st.info("💡 Por favor, carga un archivo Excel en la barra lateral. Mientras tanto, puedes previsualizar el sistema con **datos de ejemplo generados automáticamente**.")
    if st.checkbox("Usar datos de simulación/ejemplo"):
        df_pq, df_ap = cargar_datos_ejemplo()
        st.success("¡Datos de simulación cargados con éxito!")
    else:
        st.stop()
else:
    try:
        # Intentar leer las hojas especificadas por el usuario
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
    col_pq = st.selectbox("Selecciona la columna de Parqueaderos", df_pq.columns)
    lista_parqueaderos = df_pq[col_pq].dropna().astype(str).tolist()
    st.write(f"Total parqueaderos detectados: **{len(lista_parqueaderos)}**")
    st.dataframe(df_pq[[col_pq]], height=200, use_container_width=True)

with col2:
    st.subheader("🏢 Apartamentos Participantes")
    col_ap = st.selectbox("Selecciona la columna de Apartamentos", df_ap.columns)
    lista_apartamentos = df_ap[col_ap].dropna().astype(str).tolist()
    st.write(f"Total apartamentos detectados: **{len(lista_apartamentos)}**")
    st.dataframe(df_ap[[col_ap]], height=200, use_container_width=True)

# Validaciones críticas antes del sorteo
if len(lista_parqueaderos) == 0 or len(lista_apartamentos) == 0:
    st.warning("⚠️ Asegúrate de que ambas listas tengan datos válidos.")
    st.stop()

if len(lista_parqueaderos) < len(lista_apartamentos):
    st.error(f"🚨 Alerta: Hay más apartamentos ({len(lista_apartamentos)}) que parqueaderos disponibles ({len(lista_parqueaderos)}). Faltan {len(lista_apartamentos) - len(lista_parqueaderos)} parqueaderos.")
    st.stop()

# Configuración del Sorteo
st.markdown("---")
st.subheader("⚙️ Configuración del Sorteo Visual")
velocidad = st.slider("Velocidad de la animación (segundos por asignación)", min_value=0.05, max_value=1.5, value=0.3, step=0.05)

# Inicializar estados de la sesión
if "sorteo_realizado" not in st.session_state:
    st.session_state.sorteo_realizado = False
if "resultados_df" not in st.session_state:
    st.session_state.resultados_df = None

# Botón Principal
if st.button("🚀 INICIAR SORTEO PÚBLICO", type="primary"):
    st.session_state.sorteo_realizado = False
    
    # Copias para mezclar de manera segura
    ap_mezclados = lista_apartamentos.copy()
    pq_disponibles = lista_parqueaderos.copy()
    
    # Mezclamos los apartamentos de forma totalmente aleatoria
    random.shuffle(ap_mezclados)
    # Mezclamos también los parqueaderos para doble aleatoriedad
    random.shuffle(pq_disponibles)
    
    # Contenedor de la animación activa
    st.subheader("🔮 Proceso de Asignación en Tiempo Real")
    progreso_bar = st.progress(0)
    status_text = st.empty()
    
    # Cuadro visual grande de asignación de impacto
    pantalla_animacion = st.empty()
    
    # Tabla en vivo que se irá llenando
    tabla_en_vivo = st.empty()
    
    resultados_lista = []
    total_sorteos = len(ap_mezclados)
    
    for i, apto in enumerate(ap_mezclados):
        pq_asignado = pq_disponibles[i]
        
        # Efecto visual de "Ruleta" antes de fijar el resultado (simulación de giro rápido)
        for _ in range(5):
            opcion_aleatoria = random.choice(pq_disponibles[i:])
            pantalla_animacion.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; border: 2px dashed #31333F;">
                <h3 style="margin: 0; color: #555;">Sorteando Parqueadero para: <b>{apto}</b></h3>
                <h1 style="margin: 10px 0; color: #ff4b4b; font-size: 40px;">🔄 {opcion_aleatoria}</h1>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.03)
            
        # Fijar la asignación real
        resultados_lista.append({"Apartamento": apto, "Parqueadero Asignado": pq_asignado})
        
        # Mostrar el resultado fijado en grande
        pantalla_animacion.markdown(f"""
        <div style="background-color: #d4edda; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #28a745;">
            <h3 style="margin: 0; color: #155724;">¡ASIGNADO!</h3>
            <h2 style="margin: 5px 0; color: #155724;">🏢 {apto}</h2>
            <h1 style="margin: 5px 0; color: #28a745; font-size: 45px;">🚗 {pq_asignado}</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        porcentaje = int((i + 1) / total_sorteos * 100)
        progreso_bar.progress(porcentaje)
        status_text.markdown(f"Asignando: **{i+1}** de **{total_sorteos}** apartamentos.")
        
        # Actualizar tabla resumida en vivo
        df_actual = pd.DataFrame(resultados_lista)
        tabla_en_vivo.dataframe(df_actual.tail(5), use_container_width=True) # Muestra los últimos 5 asignados
        
        time.sleep(velocidad)
        
    # Limpiar pantalla de animación y dar mensaje de éxito total
    pantalla_animacion.empty()
    st.balloons()
    st.success("🎉 ¡El sorteo ha finalizado con éxito! Todos los apartamentos tienen un parqueadero asignado.")
    
    # Guardar en el estado para mantener el resultado visible si interactúan con algo más
    st.session_state.resultados_df = pd.DataFrame(resultados_lista)
    st.session_state.sorteo_realizado = True

# Mostrar Resultados Finales y Descarga si ya concluyó el sorteo
if st.session_state.sorteo_realizado and st.session_state.resultados_df is not None:
    st.markdown("---")
    st.subheader("🏆 Resultados Finales del Sorteo")
    
    res_df = st.session_state.resultados_df
    
    # Buscador para que los vecinos revisen su apartamento de inmediato
    buscar_apto = st.text_input("🔍 Buscar mi apartamento en la lista de ganadores:")
    if buscar_apto:
        df_filtrado = res_df[res_df['Apartamento'].str.contains(buscar_apto, case=False, na=False)]
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.dataframe(res_df, use_container_width=True)
        
    # Convertir a Excel en memoria para la descarga
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        res_df.to_excel(writer, index=False, sheet_name='Resultado_Sorteo')
    processed_data = output.getvalue()
    
    st.download_button(
        label="📥 Descargar Resultados en Excel",
        data=processed_data,
        file_name="resultados_sorteo_parqueaderos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
