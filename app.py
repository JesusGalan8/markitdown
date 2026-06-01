import streamlit as st
from markitdown import MarkItDown
import tempfile
import os

st.set_page_config(page_title="Mi Conversor", page_icon="📄")

st.title("Conversor MarkItDown Privado")

st.write("Sube uno o varios documentos (PDF, Word, Excel, PPT, imagen...) y extraeré el texto en Markdown.")

archivos_subidos = st.file_uploader("Arrastra aquí tus archivos", label_visibility="collapsed", accept_multiple_files=True)

if archivos_subidos:
    st.info(f"Procesando {len(archivos_subidos)} documento(s)... (puede tardar unos segundos)")
    
    md = MarkItDown()
    st.success("¡Conversión completada!")
    
    for i, archivo_subido in enumerate(archivos_subidos):
        # Guardamos el archivo temporalmente en el servidor
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(archivo_subido.name)[1]) as tmp_file:
            tmp_file.write(archivo_subido.getvalue())
            ruta_temporal = tmp_file.name

        try:
            # Ejecutamos la conversión
            resultado = md.convert(ruta_temporal)
            
            # Nombre del archivo .md a descargar
            nombre_descarga = os.path.splitext(archivo_subido.name)[0] + ".md"
            
            # Creamos una cajita para cada archivo con su botón de descarga
            with st.container():
                # Es importante que el parámetro key sea único para cada botón
                st.download_button(
                    label=f"⬇️ Descargar {nombre_descarga}",
                    data=resultado.text_content,
                    file_name=nombre_descarga,
                    mime="text/markdown",
                    key=f"btn_descarga_{i}_{nombre_descarga}"
                )
                
                # Mostramos una vista previa en la web
                with st.expander(f"Ver vista previa: {nombre_descarga}"):
                    st.code(resultado.text_content, language="markdown")
            
        except Exception as e:
            st.error(f"Fallo al leer el documento '{archivo_subido.name}': {e}")
            
        finally:
            # Limpiamos el archivo temporal del servidor
            if os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)