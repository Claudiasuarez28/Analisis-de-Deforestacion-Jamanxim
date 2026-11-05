
import os
import numpy as np
import rasterio

carpeta = "imagenes/originales"
carpeta_procesadas = "imagenes/procesadas"

def ruta_anio(anio):
    if anio == 2000:
        return os.path.join(
            carpeta_procesadas,
            "Jamanxim_2000_corregido.tif"
        )
    return os.path.join(carpeta, f"Jamanxim_{anio}.tif")


archivo_base = ruta_anio(2000)

with rasterio.open(archivo_base) as base:
    perfil = base.profile
    mascara_base = np.zeros(
        (base.height, base.width),
        dtype=bool
    )

    for _, ventana in base.block_windows(4):
        nir = base.read(4, window=ventana)
        swir2 = base.read(6, window=ventana)

        valido = np.isfinite(nir) & np.isfinite(swir2)

        if base.nodata is not None:
            if np.isnan(base.nodata):
                valido &= np.isfinite(nir) & np.isfinite(swir2)
            else:
                valido &= (nir != base.nodata) & (swir2 != base.nodata)

        filas = slice(
            int(ventana.row_off),
            int(ventana.row_off + ventana.height)
        )
        columnas = slice(
            int(ventana.col_off),
            int(ventana.col_off + ventana.width)
        )

        mascara_base[filas, columnas] = valido

print("\nCOMPARACION DE MASCARAS\n")
print("Año de referencia: 2000")

for anio in range(2001, 2020):
    with rasterio.open(ruta_anio(anio)) as src:
        diferentes = 0
        validos = 0

        for _, ventana in src.block_windows(4):
            nir = src.read(4, window=ventana)
            swir2 = src.read(6, window=ventana)

            valido = np.isfinite(nir) & np.isfinite(swir2)

            if src.nodata is not None:
                if np.isnan(src.nodata):
                    valido &= np.isfinite(nir) & np.isfinite(swir2)
                else:
                    valido &= (nir != src.nodata) & (swir2 != src.nodata)

            filas = slice(
                int(ventana.row_off),
                int(ventana.row_off + ventana.height)
            )
            columnas = slice(
                int(ventana.col_off),
                int(ventana.col_off + ventana.width)
            )

            referencia = mascara_base[filas, columnas]

            diferentes += np.count_nonzero(valido != referencia)
            validos += np.count_nonzero(valido)

    print(
        f"{anio}: píxeles válidos={validos:,} | "
        f"diferencias frente a 2000={diferentes:,}"
    )

print("\nCOMPARACION FINALIZADA")
