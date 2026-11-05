import os
import rasterio

carpeta = "imagenes/originales"

print("\nVERIFICACION DE IMAGENES SATELITALES\n")

for anio in range(2000, 2020):
    archivo = os.path.join(carpeta, f"Jamanxim_{anio}.tif")

    with rasterio.open(archivo) as imagen:
        print(f"Año: {anio}")
        print(f"  Dimensiones: {imagen.width} x {imagen.height}")
        print(f"  Bandas: {imagen.count}")
        print(f"  Resolución: {imagen.res}")
        print(f"  CRS: {imagen.crs}")
        print(f"  Tipo de dato: {imagen.dtypes[0]}")
        print(f"  NoData: {imagen.nodata}")
        print("-" * 45)

print("VERIFICACION FINALIZADA")
