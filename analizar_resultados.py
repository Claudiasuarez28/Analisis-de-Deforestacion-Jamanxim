
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Rutas
archivo = Path("resultados/tablas/area_binaria_2000_2019.csv")
carpeta = Path("resultados/graficas")
carpeta.mkdir(parents=True, exist_ok=True)

# Cargar resultados
datos = pd.read_csv(archivo)

# Identificar valores principales
mayor = datos.loc[datos["Area_segmentada_km2"].idxmax()]
menor = datos.loc[datos["Area_segmentada_km2"].idxmin()]

diferencia = mayor["Area_segmentada_km2"] - menor["Area_segmentada_km2"]

variacion = (
    datos.iloc[-1]["Area_segmentada_km2"]
    - datos.iloc[0]["Area_segmentada_km2"]
)

# Mostrar analisis
print("\nANALISIS DE RESULTADOS 2000-2019")
print("=" * 55)

print(f"Mayor area: {mayor['Area_segmentada_km2']:.2f} km2")
print(f"Anio: {int(mayor['Anio'])}")

print(f"\nMenor area: {menor['Area_segmentada_km2']:.2f} km2")
print(f"Anio: {int(menor['Anio'])}")

print(f"\nDiferencia entre mayor y menor: {diferencia:.2f} km2")
print(f"Variacion entre 2000 y 2019: {variacion:.2f} km2")

# Grafica
plt.figure(figsize=(13, 7))

plt.plot(
    datos["Anio"],
    datos["Area_segmentada_km2"],
    marker="o",
    linewidth=2,
    label="Area segmentada"
)

plt.scatter(
    mayor["Anio"],
    mayor["Area_segmentada_km2"],
    s=100,
    label="Mayor area"
)

plt.scatter(
    menor["Anio"],
    menor["Area_segmentada_km2"],
    s=100,
    label="Menor area"
)

plt.title("Evolucion del area segmentada - Jamanxim (2000-2019)")
plt.xlabel("Anio")
plt.ylabel("Area (km2)")
plt.xticks(range(2000, 2020), rotation=45)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    carpeta / "analisis_evolucion_2000_2019.png",
    dpi=300
)

plt.close()

print("\nGrafica de analisis guardada correctamente.")
