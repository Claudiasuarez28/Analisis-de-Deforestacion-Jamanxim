
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================
# CALCULO DEL AREA SEGMENTADA 2000-2019
# ==========================================

CARPETA_IMAGENES = Path("imagenes/procesadas")
CARPETA_TABLAS = Path("resultados/tablas")
CARPETA_GRAFICAS = Path("resultados/graficas")

CARPETA_TABLAS.mkdir(parents=True, exist_ok=True)
CARPETA_GRAFICAS.mkdir(parents=True, exist_ok=True)

# Resolucion espacial de las imagenes Landsat
RESOLUCION_PIXEL = 30  # metros

# Area de un pixel en kilometros cuadrados
AREA_PIXEL_KM2 = (RESOLUCION_PIXEL * RESOLUCION_PIXEL) / 1_000_000

resultados = []

print("\nCALCULO DEL AREA SEGMENTADA")
print("=" * 65)

for anio in range(2000, 2020):

    ruta = CARPETA_IMAGENES / f"Jamanxim_{anio}_binaria.png"

    if not ruta.exists():
        print(f"ERROR: No se encontro la imagen de {anio}")
        continue

    imagen = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)

    if imagen is None:
        print(f"ERROR: No se pudo leer la imagen de {anio}")
        continue

    # Contar los pixeles blancos (255)
    pixeles_blancos = int(np.count_nonzero(imagen == 255))

    # Calcular el area segmentada
    area_km2 = pixeles_blancos * AREA_PIXEL_KM2

    resultados.append({
        "Anio": anio,
        "Pixeles_blancos": pixeles_blancos,
        "Area_pixel_km2": AREA_PIXEL_KM2,
        "Area_segmentada_km2": area_km2
    })

    print(f"\nAnio: {anio}")
    print(f"Pixeles blancos: {pixeles_blancos:,}")
    print(f"Area segmentada: {area_km2:,.4f} km2")

# ==========================================
# GUARDAR RESULTADOS
# ==========================================

if len(resultados) == 0:
    print("\nNo se encontraron resultados.")
    raise SystemExit

tabla = pd.DataFrame(resultados)

ruta_csv = CARPETA_TABLAS / "area_binaria_2000_2019.csv"
tabla.to_csv(ruta_csv, index=False, encoding="utf-8-sig")

print("\n" + "=" * 65)
print("RESUMEN DEL CALCULO")
print("=" * 65)

print(tabla.to_string(index=False))

print(f"\nTabla guardada en: {ruta_csv}")

# ==========================================
# GRAFICA DE EVOLUCION
# ==========================================

plt.figure(figsize=(12, 6))

plt.plot(
    tabla["Anio"],
    tabla["Area_segmentada_km2"],
    marker="o",
    linewidth=2
)

plt.title("Area segmentada por umbralizacion (2000-2019)")
plt.xlabel("Anio")
plt.ylabel("Area segmentada (km2)")
plt.xticks(range(2000, 2020), rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()

ruta_grafica = CARPETA_GRAFICAS / "area_binaria_2000_2019.png"

plt.savefig(ruta_grafica, dpi=300)
plt.close()

print(f"Grafica guardada en: {ruta_grafica}")

print("\nCALCULO FINALIZADO")
