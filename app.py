import streamlit as st
from markitdown import MarkItDown
import tempfile
import os
import zipfile
import io

st.set_page_config(page_title="Mi Conversor", page_icon="📄")

st.title("Conversor MarkItDown Privado")

st.write("Sube uno o varios documentos (PDF, Word, Excel, PPT, imagen...) y extraeré el texto en Markdown.")

archivos_subidos = st.file_uploader("Arrastra aquí tus archivos", label_visibility="collapsed", accept_multiple_files=True)

if archivos_subidos:
    st.info(f"Procesando {len(archivos_subidos)} documento(s)... (puede tardar unos segundos)")
    
    md = MarkItDown()
    
    # Crear un buffer en memoria para el archivo ZIP
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for archivo_subido in archivos_subidos:
            # Guardamos el archivo temporalmente en el servidor
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(archivo_subido.name)[1]) as tmp_file:
                tmp_file.write(archivo_subido.getvalue())
                ruta_temporal = tmp_file.name

            try:
                # Ejecutamos la conversión
                resultado = md.convert(ruta_temporal)
                
                # Nombre del archivo .md a guardar en el zip
                nombre_descarga = os.path.splitext(archivo_subido.name)[0] + ".md"
                
                # Escribimos el contenido Markdown en el zip
                zip_file.writestr(nombre_descarga, resultado.text_content)
                
                # Mostramos una vista previa en la web
                with st.expander(f"Ver vista previa: {nombre_descarga}"):
                    st.code(resultado.text_content, language="markdown")
                
            except Exception as e:
                st.error(f"Fallo al leer el documento '{archivo_subido.name}': {e}")
                
            finally:
                # Limpiamos el archivo temporal del servidor
                if os.path.exists(ruta_temporal):
                    os.remove(ruta_temporal)
                    
    if len(archivos_subidos) > 0:
        st.success("¡Conversión completada!")
        
        # Botón para descargar el archivo ZIP con todos los .md
        st.download_button(
            label="⬇️ Descargar todos en ZIP",
            data=zip_buffer.getvalue(),
            file_name="documentos_convertidos.zip",
            mime="application/zip"
        )