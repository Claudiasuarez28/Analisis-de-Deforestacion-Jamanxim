
import os
import numpy as np
import rasterio

# Carpetas
CARPETA_ORIGINALES = "imagenes/originales"
CARPETA_PROCESADAS = "imagenes/procesadas"
CARPETA_NBR = os.path.join(CARPETA_PROCESADAS, "NBR")

NODATA_SALIDA = -9999.0

# Crear carpeta de resultados si no existe
os.makedirs(CARPETA_NBR, exist_ok=True)


def obtener_ruta(anio):

    # Para 2000 utilizamos la imagen corregida
    if anio == 2000:
        return os.path.join(
            CARPETA_PROCESADAS,
            "Jamanxim_2000_corregido.tif"
        )

    # Para 2001-2019 utilizamos las imágenes originales
    return os.path.join(
        CARPETA_ORIGINALES,
        f"Jamanxim_{anio}.tif"
    )


def calcular_nbr(anio):

    archivo_entrada = obtener_ruta(anio)

    archivo_salida = os.path.join(
        CARPETA_NBR,
        f"Jamanxim_{anio}_NBR.tif"
    )

    print(f"\nProcesando año {anio}...")

    if not os.path.exists(archivo_entrada):
        print(f"ERROR: No se encontró {archivo_entrada}")
        return

    with rasterio.open(archivo_entrada) as src:

        perfil = src.profile.copy()

        perfil.update(
            count=1,
            dtype="float32",
            nodata=NODATA_SALIDA,
            compress="deflate",
            predictor=3
        )

        total_validos = 0
        suma_nbr = 0.0
        minimo = float("inf")
        maximo = float("-inf")

        with rasterio.open(
            archivo_salida,
            "w",
            **perfil
        ) as dst:

            # Leer y procesar por bloques
            for _, ventana in src.block_windows(4):

                # Banda 4: infrarrojo cercano (NIR)
                nir = src.read(
                    4,
                    window=ventana
                ).astype(np.float32)

                # Banda 6: infrarrojo de onda corta 2 (SWIR2)
                swir2 = src.read(
                    6,
                    window=ventana
                ).astype(np.float32)

                # Identificar píxeles válidos
                valido = (
                    np.isfinite(nir) &
                    np.isfinite(swir2) &
                    (nir >= 0) &
                    (swir2 >= 0)
                )

                # Excluir valores NoData
                if src.nodata is not None:
                    if np.isnan(src.nodata):
                        valido &= (
                            np.isfinite(nir) &
                            np.isfinite(swir2)
                        )
                    else:
                        valido &= (
                            (nir != src.nodata) &
                            (swir2 != src.nodata)
                        )

                denominador = nir + swir2
                valido &= denominador != 0

                # Crear bloque de salida
                resultado = np.full(
                    nir.shape,
                    NODATA_SALIDA,
                    dtype=np.float32
                )

                # Calcular NBR
                np.divide(
                    nir - swir2,
                    denominador,
                    out=resultado,
                    where=valido
                )

                # Guardar resultado
                dst.write(
                    resultado,
                    1,
                    window=ventana
                )

                # Calcular estadísticas
                valores = resultado[valido]

                if valores.size > 0:

                    total_validos += valores.size

                    suma_nbr += np.sum(
                        valores,
                        dtype=np.float64
                    )

                    minimo = min(
                        minimo,
                        float(np.min(valores))
                    )

                    maximo = max(
                        maximo,
                        float(np.max(valores))
                    )

    if total_validos > 0:

        promedio = suma_nbr / total_validos

        print(f"Archivo: {archivo_salida}")
        print(f"Píxeles válidos: {total_validos:,}")
        print(f"NBR promedio: {promedio:.4f}")
        print(f"NBR mínimo: {minimo:.4f}")
        print(f"NBR máximo: {maximo:.4f}")

    else:
        print(f"No se encontraron píxeles válidos para {anio}")


# Procesar todos los años
print("CALCULO DEL NBR - FLORESTA NACIONAL DO JAMANXIM")
print("=" * 55)

for anio in range(2000, 2020):
    calcular_nbr(anio)

print("\n" + "=" * 55)
print("PROCESAMIENTO FINALIZADO")
