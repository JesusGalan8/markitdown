import streamlit as st
from markitdown import MarkItDown
import tempfile
import os
import zipfile
import io

st.set_page_config(page_title="Mi Conversor", page_icon="📄")

# Soporte de arrastrar y soltar desde cualquier parte de la pantalla
dnd_html = """
<style>
/* Área de carga mejorada */
[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed rgba(120, 120, 150, 0.4) !important;
    border-radius: 12px !important;
    padding: 35px 20px !important;
    background: rgba(120, 120, 150, 0.05) !important;
    transition: all 0.25s ease-in-out !important;
}

[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #6366f1 !important;
    background: rgba(99, 102, 241, 0.08) !important;
}

/* Overlay de pantalla completa al arrastrar archivos desde el explorador */
[data-testid="stFileUploaderDropzone"].global-drag-active {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    z-index: 9999999 !important;
    background: rgba(15, 23, 42, 0.88) !important;
    backdrop-filter: blur(10px) !important;
    border: 3px dashed #6366f1 !important;
    border-radius: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: copy !important;
    box-shadow: inset 0 0 60px rgba(99, 102, 241, 0.35) !important;
}

[data-testid="stFileUploaderDropzone"].global-drag-active * {
    pointer-events: none !important;
}

[data-testid="stFileUploaderDropzone"].global-drag-active::after {
    content: "📄 Suelta tus archivos aquí para convertirlos a Markdown";
    font-size: 1.8rem;
    font-weight: 700;
    color: #ffffff;
    margin-top: 16px;
    letter-spacing: -0.3px;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}
</style>

<script>
(function() {
    let targetWin = window;
    try {
        if (window.parent && window.parent.document) {
            targetWin = window.parent;
        }
    } catch (e) {
        targetWin = window;
    }

    if (targetWin.__globalDropzoneInitialized) return;
    targetWin.__globalDropzoneInitialized = true;

    let dragCounter = 0;

    function getDropzone() {
        return targetWin.document.querySelector('[data-testid="stFileUploaderDropzone"]');
    }

    function getFileInput() {
        return targetWin.document.querySelector('[data-testid="stFileUploaderDropzoneInput"]') || targetWin.document.querySelector('input[type="file"]');
    }

    // Evitar que el navegador abra el archivo al soltarlo en la ventana
    targetWin.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
    }, false);

    targetWin.addEventListener('dragenter', function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (e.dataTransfer && e.dataTransfer.types) {
            const types = Array.from(e.dataTransfer.types);
            if (types.includes('Files')) {
                dragCounter++;
                const dz = getDropzone();
                if (dz) {
                    dz.classList.add('global-drag-active');
                }
            }
        }
    }, false);

    targetWin.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dragCounter--;
        if (dragCounter <= 0) {
            dragCounter = 0;
            const dz = getDropzone();
            if (dz) {
                dz.classList.remove('global-drag-active');
            }
        }
    }, false);

    targetWin.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dragCounter = 0;
        const dz = getDropzone();
        const wasOverDropzone = dz && (e.target === dz || dz.contains(e.target));
        if (dz) {
            dz.classList.remove('global-drag-active');
        }

        // Si por alguna razón el drop ocurrió fuera del elemento exacto, transferir archivos al input
        if (!wasOverDropzone) {
            const files = e.dataTransfer ? e.dataTransfer.files : null;
            if (files && files.length > 0) {
                const fileInput = getFileInput();
                if (fileInput) {
                    fileInput.files = files;
                    fileInput.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        }
    }, false);
})();
</script>
"""

if hasattr(st, "html"):
    st.html(dnd_html, unsafe_allow_javascript=True)
else:
    import streamlit.components.v1 as components
    components.html(dnd_html, height=0)

st.title("Conversor MarkItDown Privado")

st.write("Arrastra y suelta uno o varios documentos en cualquier parte de la pantalla (PDF, Word, Excel, PPT, imagen...) para extraer su texto en Markdown.")

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