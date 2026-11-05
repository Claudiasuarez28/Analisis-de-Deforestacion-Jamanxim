
import ee

# ==========================================
# 1. CONECTAR CON GOOGLE EARTH ENGINE
# ==========================================

ee.Initialize(project="parcial-deforestacion")

print("Conexion exitosa con Google Earth Engine")


# ==========================================
# 2. CARGAR EL AREA DE ESTUDIO
# ==========================================

areas = ee.FeatureCollection(
    "WCMC/WDPA/current/polygons"
).filter(
    ee.Filter.eq("ISO3", "BRA")
)

jamanxim = areas.filter(
    ee.Filter.eq("NAME", "Floresta Nacional Do Jamanxim")
)

geometria = ee.Feature(
    jamanxim.first()
).geometry()

print("Area de estudio cargada correctamente")


# ==========================================
# 3. DEFINIR BANDAS DE CADA SATELITE
# ==========================================

nombres_bandas = [
    "azul",
    "verde",
    "rojo",
    "infrarrojo",
    "infrarrojo_onda_corta_1",
    "infrarrojo_onda_corta_2"
]

# Landsat 5 y 7
bandas_l57 = [
    "SR_B1",
    "SR_B2",
    "SR_B3",
    "SR_B4",
    "SR_B5",
    "SR_B7"
]

# Landsat 8
bandas_l8 = [
    "SR_B2",
    "SR_B3",
    "SR_B4",
    "SR_B5",
    "SR_B6",
    "SR_B7"
]


# ==========================================
# 4. FUNCION DE PREPROCESAMIENTO
# ==========================================

def preparar_landsat(imagen, bandas_origen, bits_nubes):

    # Seleccionar banda de calidad
    qa = imagen.select("QA_PIXEL")

    # Crear mascara inicial
    mascara = qa.bitwiseAnd(1 << 0).eq(0)

    # Eliminar pixeles con nubes y sombras
    for bit in bits_nubes:
        mascara = mascara.And(
            qa.bitwiseAnd(1 << bit).eq(0)
        )

    # Eliminar pixeles saturados
    mascara_saturacion = imagen.select(
        "QA_RADSAT"
    ).eq(0)

    # Corregir reflectancia
    bandas = (
        imagen.select(bandas_origen)
        .multiply(0.0000275)
        .add(-0.2)
        .rename(nombres_bandas)
    )

    return (
        bandas
        .updateMask(mascara)
        .updateMask(mascara_saturacion)
        .copyProperties(
            imagen,
            ["system:time_start"]
        )
    )


# ==========================================
# 5. CARGAR COLECCIONES LANDSAT
# ==========================================

landsat5 = ee.ImageCollection(
    "LANDSAT/LT05/C02/T1_L2"
)

landsat7 = ee.ImageCollection(
    "LANDSAT/LE07/C02/T1_L2"
)

landsat8 = ee.ImageCollection(
    "LANDSAT/LC08/C02/T1_L2"
)


# ==========================================
# 6. CONSULTAR TAREAS EXISTENTES
# ==========================================

tareas_existentes = {}

for tarea in ee.batch.Task.list():

    estado = tarea.status()

    descripcion = estado.get("description")

    if descripcion:
        tareas_existentes[descripcion] = estado.get("state")


# ==========================================
# 7. DESCARGAR IMAGENES DE 2001 A 2019
# ==========================================

for anio in range(2001, 2020):

    print("\n================================")
    print("PROCESANDO ANIO:", anio)
    print("================================")

    descripcion = f"Jamanxim_{anio}"

    # Evitar exportaciones duplicadas
    estado_anterior = tareas_existentes.get(descripcion)

    if estado_anterior in ["READY", "RUNNING", "COMPLETED"]:

        print("Esta imagen ya tiene una tarea activa o completada.")
        print("Estado:", estado_anterior)
        continue

    # Seleccionar colecciones segun el anio
    if anio <= 2012:

        coleccion = (
            landsat5
            .merge(landsat7)
        )

        bandas_origen = bandas_l57

        bits_nubes = [1, 3, 4, 5]

    else:

        coleccion = landsat8

        bandas_origen = bandas_l8

        bits_nubes = [1, 2, 3, 4, 5]

    # Filtrar imagenes por territorio y fecha
    coleccion = (
        coleccion
        .filterBounds(geometria)
        .filterDate(
            f"{anio}-01-01",
            f"{anio + 1}-01-01"
        )
    )

    cantidad = coleccion.size().getInfo()

    print("Escenas disponibles:", cantidad)

    if cantidad == 0:

        print("No hay escenas disponibles para este anio.")
        continue

    # Aplicar preprocesamiento
    coleccion_procesada = coleccion.map(
        lambda imagen: preparar_landsat(
            imagen,
            bandas_origen,
            bits_nubes
        )
    )

    # Crear composicion mediana anual
    imagen_anual = (
        coleccion_procesada
        .median()
        .clip(geometria)
        .toFloat()
        .unmask(-9999)
    )

    print("Composicion anual creada:", anio)

    # ======================================
    # 8. EXPORTAR A GOOGLE DRIVE
    # ======================================

    tarea = ee.batch.Export.image.toDrive(

        image=imagen_anual,

        description=descripcion,

        folder="PARCIAL_DEFORESTACION",

        fileNamePrefix=descripcion,

        region=geometria,

        scale=30,

        crs="EPSG:31981",

        maxPixels=1e13,

        fileFormat="GeoTIFF",

        formatOptions={
            "noData": -9999
        }
    )

    tarea.start()

    print("Exportacion iniciada:", descripcion)
    print("Estado:", tarea.status()["state"])


print("\n================================")
print("PROCESO DE EXPORTACION FINALIZADO")
print("Revisa las tareas en Google Earth Engine.")
print("================================")
