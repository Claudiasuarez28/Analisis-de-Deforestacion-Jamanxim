
import os
import cv2
import numpy as np
import rasterio
import matplotlib.pyplot as plt

# Carpetas del proyecto
CARPETA_ORIGINALES = "imagenes/originales"
CARPETA_PROCESADAS = "imagenes/procesadas"
CARPETA_GRAFICAS = "resultados/graficas"

os.makedirs(CARPETA_PROCESADAS, exist_ok=True)
os.makedirs(CARPETA_GRAFICAS, exist_ok=True)


def normalizar_imagen(banda, mascara):
    """Convierte reflectancias válidas a escala de grises de 8 bits."""
    valores = banda[mascara]

    if valores.size == 0:
        raise ValueError("La imagen no contiene píxeles válidos.")

    minimo, maximo = np.percentile(valores, [2, 98])

    if maximo <= minimo:
        raise ValueError("No hay suficiente variación de intensidad.")

    resultado = np.zeros(banda.shape, dtype=np.uint8)

    normalizada = np.clip(
        (banda[mascara] - minimo) / (maximo - minimo) * 255,
        0,
        255
    )

    resultado[mascara] = normalizada.astype(np.uint8)

    return resultado


def guardar_imagen(ruta, imagen):
    cv2.imwrite(ruta, imagen)


def procesar_anio(anio):
    archivo = os.path.join(
        CARPETA_ORIGINALES,
        f"Jamanxim_{anio}.tif"
    )

    if anio == 2000:
        archivo = os.path.join(
            CARPETA_PROCESADAS,
            "Jamanxim_2000_corregido.tif"
        )

    print(f"\nProcesando año {anio}...")

    with rasterio.open(archivo) as src:
        banda = src.read(3).astype(np.float32)
        mascara = np.isfinite(banda)

        if src.nodata is not None and not np.isnan(src.nodata):
            mascara &= banda != src.nodata

        gris = normalizar_imagen(banda, mascara)

        # Ecualización del histograma
        ecualizada = cv2.equalizeHist(gris)

        # Ajuste de contraste y brillo
        contraste = cv2.convertScaleAbs(
            gris,
            alpha=1.3,
            beta=15
        )

        # Umbralización automática de Otsu
        _, binaria = cv2.threshold(
            ecualizada,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Operaciones morfológicas
        kernel = np.ones((3, 3), np.uint8)

        apertura = cv2.morphologyEx(
            binaria,
            cv2.MORPH_OPEN,
            kernel
        )

        cierre = cv2.morphologyEx(
            apertura,
            cv2.MORPH_CLOSE,
            kernel
        )

        # Restaurar los píxeles sin información a cero
        gris[~mascara] = 0
        ecualizada[~mascara] = 0
        contraste[~mascara] = 0
        binaria[~mascara] = 0
        cierre[~mascara] = 0

    # Guardar imágenes procesadas
    resultados = {
        "grises": gris,
        "ecualizada": ecualizada,
        "contraste": contraste,
        "binaria": binaria,
        "morfologica": cierre
    }

    for nombre, imagen in resultados.items():
        ruta = os.path.join(
            CARPETA_PROCESADAS,
            f"Jamanxim_{anio}_{nombre}.png"
        )
        guardar_imagen(ruta, imagen)

    # Crear gráfica comparativa
    fig, ejes = plt.subplots(2, 3, figsize=(16, 10))

    titulos = [
        "Escala de grises",
        "Ecualización",
        "Brillo y contraste",
        "Umbralización",
        "Operaciones morfológicas"
    ]

    for eje, (nombre, imagen), titulo in zip(
        ejes.flat,
        resultados.items(),
        titulos
    ):
        eje.imshow(imagen, cmap="gray", vmin=0, vmax=255)
        eje.set_title(titulo)
        eje.axis("off")

    # Ocultar el sexto espacio
    ejes.flat[5].axis("off")

    fig.suptitle(
        f"Procesamiento de imagen satelital - {anio}",
        fontsize=16
    )

    plt.tight_layout()

    ruta_grafica = os.path.join(
        CARPETA_GRAFICAS,
        f"procesamiento_{anio}.png"
    )

    plt.savefig(ruta_grafica, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"Año {anio} terminado correctamente.")


# Procesar los 20 años
for anio in range(2000, 2020):
    try:
        procesar_anio(anio)
    except Exception as error:
        print(f"ERROR en {anio}: {error}")

print("\nPROCESAMIENTO FINALIZADO.")
