
import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt

# Carpetas
CARPETA_NBR = "imagenes/procesadas/NBR"
CARPETA_MAPAS = os.path.join(CARPETA_NBR, "mapas")

os.makedirs(CARPETA_MAPAS, exist_ok=True)

# Escala común para comparar todos los años
MIN_NBR = -0.3
MAX_NBR = 1.0

print("GENERANDO MAPAS NBR")
print("=" * 50)

for anio in range(2000, 2020):

    archivo_entrada = os.path.join(
        CARPETA_NBR,
        f"Jamanxim_{anio}_NBR.tif"
    )

    archivo_salida = os.path.join(
        CARPETA_MAPAS,
        f"Mapa_NBR_{anio}.png"
    )

    print(f"\nGenerando mapa del año {anio}...")

    if not os.path.exists(archivo_entrada):
        print(f"No se encontró: {archivo_entrada}")
        continue

    with rasterio.open(archivo_entrada) as src:

        # Leer el índice NBR
        nbr = src.read(1)

        # Identificar valores válidos
        valido = (
            np.isfinite(nbr) &
            (nbr != src.nodata)
        )

        # Crear imagen con valores NoData transparentes
        imagen = np.ma.masked_where(
            ~valido,
            nbr
        )

        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 8))

        mapa = ax.imshow(
            imagen,
            cmap="RdYlGn",
            vmin=MIN_NBR,
            vmax=MAX_NBR
        )

        # Barra de colores
        barra = fig.colorbar(
            mapa,
            ax=ax,
            shrink=0.75
        )

        barra.set_label("Índice NBR")

        ax.set_title(
            f"Índice NBR - Floresta Nacional do Jamanxim ({anio})",
            fontsize=13
        )

        ax.set_xlabel("Columnas de píxeles")
        ax.set_ylabel("Filas de píxeles")

        ax.set_axis_off()

        plt.tight_layout()

        plt.savefig(
            archivo_salida,
            dpi=200,
            bbox_inches="tight"
        )

        plt.close(fig)

    print(f"Mapa guardado: {archivo_salida}")

print("\n" + "=" * 50)
print("GENERACION DE MAPAS FINALIZADA")
