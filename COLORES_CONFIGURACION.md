# Configuración de Colores - Comparativa

## Paleta de Colores ETSISI vs Anterior

### Colores Principales

| Elemento | Color Anterior | Color ETSISI | Cambio |
|----------|---------------|--------------|---------|
| **Azul Principal** | `#003d6b` | `#003366` | ✅ Más oscuro, más institucional |
| **Azul Medio** | `#005a9c` | `#005B99` | ✅ Prácticamente igual |
| **Azul Claro** | `#0077c8` | `#0077c8` | ⚪ Sin cambios |

### Colores de Texto

| Elemento | Color Anterior | Color ETSISI | Cambio |
|----------|---------------|--------------|---------|
| **Texto Normal** | `#333` | `#787878` | ✅ Más gris, según guía ETSISI |
| **Texto Inactivo** | `#666` / `#999` | `#999999` | ✅ Unificado según guía |

### Colores de Fondo

| Elemento | Color Anterior | Color ETSISI | Cambio |
|----------|---------------|--------------|---------|
| **Fondo Normal** | `white` / `#FFFFFF` | `#FFFFFF` | ⚪ Sin cambios |
| **Fondo Header** | `#003d6b` | `#003366` | ✅ Actualizado a azul oscuro oficial |
| **Fondo Botón Inactivo** | `#6c757d` | `#678CA6` | ✅ Según guía ETSISI |

### Colores de Estado (Sin cambios)

| Elemento | Color |
|----------|-------|
| **Éxito** | `#28a745` (verde) |
| **Advertencia** | `#ffc107` (amarillo) |
| **Peligro/Error** | `#dc3545` (rojo) |
| **Información** | `#17a2b8` (cyan) |

## Tipografía

| Elemento | Valor Anterior | Valor ETSISI |
|----------|---------------|--------------|
| **Fuente Principal** | System fonts | `Oswald-Regular.ttf` |
| **Tamaño Base** | `1rem` (16px) | `64pt` (configurable) |

## Ubicación de la Configuración

Los colores están centralizados en:
- **Archivo**: `/app/stepup_config/settings.py`
- **Variable**: `THEME_COLORS` (diccionario)
- **Context Processor**: `theme_context()` - disponible en todos los templates

## Uso en Templates

### Antes:
```html
<div style="color: #003d6b;">Texto</div>
```

### Ahora:
```html
<div style="color: {{ THEME_COLORS.primary }};">Texto</div>
```

## Ventajas del Nuevo Sistema

✅ **Centralizado**: Un único lugar para todos los colores
✅ **Consistente**: Todos los templates usan la misma paleta
✅ **Mantenible**: Cambiar un color lo actualiza en toda la app
✅ **Corporativo**: Colores oficiales de ETSISI-UPM
✅ **Escalable**: Fácil agregar nuevos colores al diccionario

## Elementos Actualizados

- ✅ `base.html` - Header, footer, estilos globales
- ✅ `dashboard_profesor.html` - Todos los colores principales
- ✅ `seleccionar_modo.html` - Colores de la UI de selección
- ⏳ `dashboard_alumno.html` - Pendiente de actualizar
- ⏳ `realizar_test.html` - Pendiente de actualizar
- ⏳ `resultado.html` - Pendiente de actualizar

## Próximos Pasos

1. Actualizar templates de alumno con `THEME_COLORS`
2. Actualizar templates de tests y resultados
3. Considerar agregar tema oscuro usando el mismo sistema
4. Documentar guía de estilos completa basada en ETSISI
