
import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt

# Carpetas
CARPETA_NBR = "imagenes/procesadas/NBR"
CARPETA_CAMBIOS = os.path.join(CARPETA_NBR, "cambios")

os.makedirs(CARPETA_CAMBIOS, exist_ok=True)

print("CALCULO DE CAMBIOS NBR")
print("=" * 55)

for anio in range(2000, 2019):

    anio_siguiente = anio + 1

    archivo_anterior = os.path.join(
        CARPETA_NBR,
        f"Jamanxim_{anio}_NBR.tif"
    )

    archivo_actual = os.path.join(
        CARPETA_NBR,
        f"Jamanxim_{anio_siguiente}_NBR.tif"
    )

    archivo_salida = os.path.join(
        CARPETA_CAMBIOS,
        f"Cambio_NBR_{anio}_{anio_siguiente}.tif"
    )

    archivo_png = os.path.join(
        CARPETA_CAMBIOS,
        f"Mapa_Cambio_{anio}_{anio_siguiente}.png"
    )

    print(f"\nComparando {anio} con {anio_siguiente}...")

    with rasterio.open(archivo_anterior) as src1, \
         rasterio.open(archivo_actual) as src2:

        # Verificar que las imágenes coincidan espacialmente
        if (
            src1.width != src2.width or
            src1.height != src2.height or
            src1.transform != src2.transform or
            src1.crs != src2.crs
        ):
            raise ValueError(
                f"Las imágenes {anio} y {anio_siguiente} "
                "no coinciden espacialmente."
            )

        perfil = src1.profile.copy()

        perfil.update(
            count=1,
            dtype="float32",
            nodata=-9999.0,
            compress="deflate",
            predictor=3
        )

        cantidad_validos = 0
        suma_cambios = 0.0
        positivos = 0
        negativos = 0

        # Crear archivo de diferencia
        with rasterio.open(
            archivo_salida,
            "w",
            **perfil
        ) as dst:

            for _, ventana in src1.block_windows(1):

                nbr_anterior = src1.read(
                    1,
                    window=ventana
                )

                nbr_actual = src2.read(
                    1,
                    window=ventana
                )

                valido = (
                    np.isfinite(nbr_anterior) &
                    np.isfinite(nbr_actual) &
                    (nbr_anterior != src1.nodata) &
                    (nbr_actual != src2.nodata)
                )

                resultado = np.full(
                    nbr_anterior.shape,
                    -9999.0,
                    dtype=np.float32
                )

                np.subtract(
                    nbr_anterior,
                    nbr_actual,
                    out=resultado,
                    where=valido
                )

                dst.write(
                    resultado,
                    1,
                    window=ventana
                )

                valores = resultado[valido]

                cantidad_validos += valores.size
                suma_cambios += np.sum(
                    valores,
                    dtype=np.float64
                )

                positivos += np.count_nonzero(valores > 0)
                negativos += np.count_nonzero(valores < 0)

    promedio = suma_cambios / cantidad_validos

    print(f"Píxeles comparados: {cantidad_validos:,}")
    print(f"Cambio promedio: {promedio:.5f}")
    print(f"Píxeles con disminución del NBR: {positivos:,}")
    print(f"Píxeles con aumento del NBR: {negativos:,}")

    # Generar mapa PNG
    with rasterio.open(archivo_salida) as src:

        cambio = src.read(1)

        valido = (
            np.isfinite(cambio) &
            (cambio != src.nodata)
        )

        imagen = np.ma.masked_where(
            ~valido,
            cambio
        )

        fig, ax = plt.subplots(figsize=(10, 8))

        mapa = ax.imshow(
            imagen,
            cmap="RdYlGn_r",
            vmin=-0.5,
            vmax=0.5
        )

        barra = fig.colorbar(
            mapa,
            ax=ax,
            shrink=0.75
        )

        barra.set_label("Diferencia NBR")

        ax.set_title(
            f"Cambio NBR {anio}-{anio_siguiente}",
            fontsize=13
        )

        ax.set_axis_off()

        plt.tight_layout()

        plt.savefig(
            archivo_png,
            dpi=200,
            bbox_inches="tight"
        )

        plt.close(fig)

    print(f"Mapa guardado: {archivo_png}")

print("\n" + "=" * 55)
print("COMPARACION DE LOS 19 PERIODOS FINALIZADA")
