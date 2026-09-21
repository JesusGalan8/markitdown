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
    documentos_convertidos = []
    
    for archivo_subido in archivos_subidos:
        # Guardamos el archivo temporalmente en el servidor
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(archivo_subido.name)[1]) as tmp_file:
            tmp_file.write(archivo_subido.getvalue())
            ruta_temporal = tmp_file.name

        try:
            # Ejecutamos la conversión
            resultado = md.convert(ruta_temporal)
            
            # Nombre del archivo .md
            nombre_descarga = os.path.splitext(archivo_subido.name)[0] + ".md"
            documentos_convertidos.append((nombre_descarga, resultado.text_content))
            
            # Mostramos una vista previa en la web
            with st.expander(f"Ver vista previa: {nombre_descarga}"):
                st.code(resultado.text_content, language="markdown")
            
        except Exception as e:
            st.error(f"Fallo al leer el documento '{archivo_subido.name}': {e}")
            
        finally:
            # Limpiamos el archivo temporal del servidor
            if os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)
                
    if documentos_convertidos:
        st.success("¡Conversión completada!")
        
        # Si se subió un solo documento, se ofrece la descarga directa en Markdown
        if len(archivos_subidos) == 1:
            nombre_descarga, contenido = documentos_convertidos[0]
            st.download_button(
                label=f"⬇️ Descargar {nombre_descarga}",
                data=contenido,
                file_name=nombre_descarga,
                mime="text/markdown"
            )
        else:
            # Si se subieron varios documentos, se empaquetan en un archivo ZIP
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                nombres_usados = set()
                for nombre_descarga, contenido in documentos_convertidos:
                    nombre_final = nombre_descarga
                    contador = 1
                    while nombre_final in nombres_usados:
                        base, ext = os.path.splitext(nombre_descarga)
                        nombre_final = f"{base}_{contador}{ext}"
                        contador += 1
                    nombres_usados.add(nombre_final)
                    zip_file.writestr(nombre_final, contenido)
            
            # Botón para descargar el archivo ZIP con todos los .md
            st.download_button(
                label="⬇️ Descargar todos en ZIP",
                data=zip_buffer.getvalue(),
                file_name="documentos_convertidos.zip",
                mime="application/zip"
            )