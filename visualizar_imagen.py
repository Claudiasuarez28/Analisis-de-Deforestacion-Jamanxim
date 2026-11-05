
import rasterio
import numpy as np
import matplotlib.pyplot as plt

from rasterio.enums import Resampling

# ==========================================
# 1. ABRIR IMAGEN SATELITAL
# ==========================================

ruta = "imagenes/originales/Jamanxim_2000.tif"

with rasterio.open(ruta) as imagen:

    # Leer bandas RGB con menor resolucion
    rgb = imagen.read(
        [3, 2, 1],
        out_shape=(
            3,
            imagen.height // 4,
            imagen.width // 4
        ),
        resampling=Resampling.average,
        masked=True
    )

# ==========================================
# 2. AJUSTAR CONTRASTE PARA VISUALIZACION
# ==========================================

canales = []

for banda in rgb:

    valores = banda.compressed()

    minimo, maximo = np.percentile(
        valores, [2, 98]
    )

    canal = np.clip(
        (banda - minimo) / (maximo - minimo),
        0,
        1
    )

    canales.append(canal.filled(0))

imagen_rgb = np.dstack(canales)

# ==========================================
# 3. MOSTRAR IMAGEN
# ==========================================

plt.figure(figsize=(12, 9))

plt.imshow(imagen_rgb)

plt.title(
    "Floresta Nacional Do Jamanxim - Año 2000"
)

plt.axis("off")

plt.tight_layout()

# Guardar resultado
plt.savefig(
    "resultados/graficas/imagen_2000_original.png",
    dpi=200,
    bbox_inches="tight"
)

plt.show()

print("Imagen visualizada correctamente")
print("Vista guardada en resultados/graficas")
