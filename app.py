import streamlit as st
from markitdown import MarkItDown
import tempfile
import os

st.set_page_config(page_title="Mi Conversor", page_icon="📄")

st.title("Conversor MarkItDown Privado")

# --- SISTEMA DE SEGURIDAD ---
# ¡IMPORTANTE! Cambia "1234" por la contraseña que tú quieras usar
PASSWORD_SECRETA = "1234" 

def comprobar_contrasena():
    if "acceso_concedido" not in st.session_state:
        st.session_state["acceso_concedido"] = False

    if not st.session_state["acceso_concedido"]:
        pwd_usuario = st.text_input("Introduce la contraseña para acceder:", type="password")
        if st.button("Entrar"):
            if pwd_usuario == PASSWORD_SECRETA:
                st.session_state["acceso_concedido"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
        return False
    return True
# ----------------------------

# Si la contraseña es correcta, mostramos la herramienta
if comprobar_contrasena():
    st.write("Sube cualquier documento (PDF, Word, Excel, PPT, imagen...) y extraeré el texto en Markdown.")
    
    archivo_subido = st.file_uploader("Arrastra aquí tu archivo", label_visibility="collapsed")

    if archivo_subido is not None:
        # Guardamos el archivo temporalmente en el servidor
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(archivo_subido.name)[1]) as tmp_file:
            tmp_file.write(archivo_subido.getvalue())
            ruta_temporal = tmp_file.name

        st.info("Procesando documento... (puede tardar unos segundos)")
        
        md = MarkItDown()
        try:
            # Ejecutamos la conversión
            resultado = md.convert(ruta_temporal)
            st.success("¡Conversión completada!")
            
            # Botón para descargar el archivo .md
            nombre_descarga = os.path.splitext(archivo_subido.name)[0] + ".md"
            st.download_button(
                label="⬇️ Descargar texto en Markdown",
                data=resultado.text_content,
                file_name=nombre_descarga,
                mime="text/markdown"
            )
            
            # Mostramos una vista previa en la web
            with st.expander("Ver vista previa del texto extraído"):
                st.code(resultado.text_content, language="markdown")
            
        except Exception as e:
            st.error(f"Fallo al leer el documento: {e}")
            
        finally:
            # Limpiamos el archivo temporal del servidor
            if os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)