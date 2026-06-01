# Sección I – Introducción

##  Propósito del Proyecto

Este proyecto tiene como objetivo comparar el rendimiento y las capacidades de distintos sistemas de bases de datos relacionales y no relacionales (SQL y NoSQL) a través de un caso práctico: un sistema de reservas de hoteles.

La idea es simular un entorno realista de datos que permita probar:

- Velocidad de carga (ingesta)
- Eficiencia en consultas
- Adaptabilidad a estructuras jerárquicas
- Representación en distintos modelos (relacional, documento, grafo, columna)

---

## ¿Qué se está modelando?

El dominio del problema es un sistema hotelero multinivel, compuesto por:

- **Países**: Agrupación geográfica y monetaria
- **Cadenas hoteleras**: Marcas corporativas
- **Hoteles**: Unidades operativas
- **Habitaciones**: Inventario físico
- **Huéspedes**: Clientes
- **Servicios**: Add-ons disponibles
- **Reservas**: Transacciones principales

Este sistema se implementa en diferentes motores de base de datos:

| Tecnología | Tipo       | Rol en el proyecto                      |
|------------|------------|------------------------------------------|
| MySQL      | Relacional | Estructura clásica en tablas normalizadas |
| MongoDB    | Documento  | JSON anidado por jerarquía                |
| Neo4j      | Grafo      | Relaciones huésped–hotel–servicio         |
| BigQuery   | Columna    | Procesamiento analítico a gran escala     |

---

## Alcance de esta sección

En esta primera sección se presentan:

- El contexto del proyecto
- Los objetivos generales
- La motivación para el uso de distintas tecnologías
- Una visión general del dominio modelado

---

## Archivos en esta carpeta

Este directorio no contiene archivos técnicos; solo sirve como punto de partida para entender el enfoque del proyecto. Consulta la Sección 2 para el modelo de datos completo.

---

## Autor

Luis Anthony Flores Portillo  
Estudiante de Ciencia de Datos

