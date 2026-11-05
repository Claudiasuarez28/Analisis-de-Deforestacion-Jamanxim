import rasterio
import numpy as np
import os

entrada = "imagenes/originales/Jamanxim_2000.tif"
salida = "imagenes/procesadas/Jamanxim_2000_corregido.tif"

with rasterio.open(entrada) as origen:

    perfil = origen.profile.copy()

    perfil.update(
        dtype="float32",
        nodata=np.nan,
        compress="deflate",
        predictor=3
    )

    with rasterio.open(salida, "w", **perfil) as destino:

        for ventana in origen.block_windows(1):

            bloque = origen.read(window=ventana[1])

            destino.write(
                bloque.astype("float32"),
                window=ventana[1]
            )

print("Imagen corregida correctamente.")

with rasterio.open(salida) as imagen:

    print("NoData:", imagen.nodata)
    print("Dimensiones:", imagen.width, "x", imagen.height)
    print("Bandas:", imagen.count)
    print("Resolución:", imagen.res)
    print("Tamaño:", round(os.path.getsize(salida) / 1048576, 2), "MB")