# Templates Reutilizables - Dashboard Profesor

## boton_anadir.html

Template reutilizable para botones de añadir elementos **en tablas**.

### Uso

```django
{% include 'boards/profesor/includes/boton_anadir.html' with titulo='Añadir tema' onclick='mostrarModalCrearTema()' colspan=8 %}
```

### Parámetros

- **titulo** (opcional): Texto que aparecerá en el botón. Si se omite, solo muestra "+"
- **onclick** (requerido): Función JavaScript a ejecutar al hacer clic (sin `return false;`, se añade automáticamente)
- **colspan** (opcional): Número de columnas que ocupará el botón. Default: 8
- **tooltip** (opcional): Texto del tooltip. Si no se especifica, usa el valor de `titulo`

### Ejemplos

```django
{# Botón con texto completo #}
{% include 'boards/profesor/includes/boton_anadir.html' with titulo='tema' onclick='mostrarModalCrearTema()' colspan=8 %}
{# Resultado: "Añadir tema" #}

{# Botón solo con símbolo + #}
{% include 'boards/profesor/includes/boton_anadir.html' with onclick='mostrarModal()' colspan=8 %}
{# Resultado: "+" #}

{# Con tooltip personalizado #}
{% include 'boards/profesor/includes/boton_anadir.html' with titulo='test' onclick='mostrarModalCrearTest()' colspan=10 tooltip='Crear nuevo test' %}

{# Para tabla con menos columnas #}
{% include 'boards/profesor/includes/boton_anadir.html' with titulo='pregunta' onclick='mostrarModalCrearPregunta()' colspan=5 %}
```

### Características

- **Diseño responsive**: El botón se ajusta automáticamente al contenido del texto
- **Efectos hover**: Cambio de color y escala al pasar el ratón
- **Icono integrado**: Emoji ➕ antes del texto
- **Centrado**: El botón siempre aparece centrado en la fila

---

### Características

- **Diseño responsive**: El botón se ajusta automáticamente al contenido del texto
- **Efectos hover**: Cambio de color y escala al pasar el ratón
- **Icono integrado**: Emoji ➕ antes del texto
- **Alineación flexible**: Puede estar centrado, a la izquierda o derecha
- **Sin estructura de tabla**: Perfecto para formularios y secciones libres

---

## Estilo Común

Ambos templates utilizan los mismos colores del tema:
- Color de fondo: `THEME_COLORS.primary_light`
- Color hover: `#00a8e8`
- Transiciones suaves para mejor experiencia de usuario
- Tamaño de fuente: 1rem (tablas) o 0.95rem (simples)
- Efectos de escala: `scale(1.05)` en hover
