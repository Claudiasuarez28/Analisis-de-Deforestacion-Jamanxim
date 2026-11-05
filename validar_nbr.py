
import os
import numpy as np
import rasterio

carpeta = "imagenes/originales"

print("\nVALIDACION DEL INDICE NBR - 2000 A 2019\n")

for anio in range(2000, 2020):

    archivo = os.path.join(carpeta, f"Jamanxim_{anio}.tif")

    with rasterio.open(archivo) as src:
        nir = src.read(4).astype(np.float32)
        swir2 = src.read(6).astype(np.float32)

        mascara = np.isfinite(nir) & np.isfinite(swir2)

        if src.nodata is not None:
            if np.isnan(src.nodata):
                mascara &= np.isfinite(nir) & np.isfinite(swir2)
            else:
                mascara &= (nir != src.nodata) & (swir2 != src.nodata)

        nir = nir[mascara]
        swir2 = swir2[mascara]

        total = len(nir)

        negativos = (nir < 0) | (swir2 < 0)
        denominador = nir + swir2

        validos = (
            (nir >= 0) &
            (swir2 >= 0) &
            (denominador > 1e-6)
        )

        nbr = (
            (nir[validos] - swir2[validos]) /
            (nir[validos] + swir2[validos])
        )

        fuera_rango = np.sum((nbr < -1) | (nbr > 1))

        print(f"AÑO {anio}")
        print(f"  Píxeles disponibles: {total:,}")
        print(f"  Reflectancias negativas: {np.sum(negativos):,}")
        print(f"  Píxeles utilizables para NBR: {len(nbr):,}")
        print(f"  NBR promedio: {np.mean(nbr):.4f}")
        print(f"  NBR fuera de [-1, 1]: {fuera_rango:,}")
        print("-" * 45)

print("VALIDACION TERMINADA")

