
import os
import numpy as np
import rasterio

carpeta = "imagenes/originales"

print("\nANALISIS ESPECTRAL DE LAS IMAGENES\n")

for anio in [2000, 2005, 2010, 2015, 2019]:

    archivo = os.path.join(carpeta, f"Jamanxim_{anio}.tif")

    with rasterio.open(archivo) as src:

        nir = src.read(4).astype(np.float32)
        swir2 = src.read(6).astype(np.float32)

        mascara = np.isfinite(nir) & np.isfinite(swir2)

        if src.nodata is not None:
            mascara &= (nir != src.nodata) & (swir2 != src.nodata)

        nir = nir[mascara]
        swir2 = swir2[mascara]

        denominador = nir + swir2
        valido = np.abs(denominador) > 1e-6

        nbr = (nir[valido] - swir2[valido]) / denominador[valido]

        print(f"AÑO {anio}")
        print(f"  Píxeles válidos: {len(nbr):,}")
        print(f"  NIR promedio: {np.mean(nir):.4f}")
        print(f"  SWIR2 promedio: {np.mean(swir2):.4f}")
        print(f"  NBR promedio: {np.mean(nbr):.4f}")
        print(f"  NBR mínimo: {np.min(nbr):.4f}")
        print(f"  NBR máximo: {np.max(nbr):.4f}")
        print("-" * 45)

print("ANALISIS FINALIZADO")
