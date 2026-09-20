# Portafolio — Miguel Villalba

Sitio personal de Miguel Villalba, Senior Backend & Full Stack Developer (APIs, integraciones e interoperabilidad en salud con HL7 FHIR).

Sitio estático en HTML, CSS y JavaScript vanilla, sin frameworks, sin jQuery y sin paso de build.

## Estructura

```
portafolio/
├── index.html          # Página única (todas las secciones)
└── assets/
    ├── css/style.css   # Sistema de diseño (tokens, componentes, responsive)
    ├── js/main.js      # Interacciones (menú, scrollspy, reveal, filtros, contadores)
    └── img/            # Favicons, foto de perfil y capturas de proyectos
```

## Secciones

Inicio · Sobre mí · Estadísticas · Stack técnico · Experiencia · Proyectos (con filtros) · Servicios · Contacto.

## Ejecutar en local

No requiere instalación. Abre `index.html` en el navegador, o sirve la carpeta con cualquier servidor estático:

```bash
python -m http.server 8000
# luego abrir http://localhost:8000
```

## Cómo editar

- **Contenido:** directamente en `index.html`. Cada sección está delimitada por un comentario `<!-- ======= Nombre ======= -->`.
- **Colores y tipografía:** variables CSS en `:root` al inicio de `assets/css/style.css`.
- **Estadísticas animadas:** el atributo `data-count` define el número final y `data-suffix` un sufijo opcional (por ejemplo `+`).
- **Proyectos:** cada tarjeta es un `<article class="project-card" data-category="...">`. Las categorías del filtro son `health`, `web` y `systems`.
- **Textos del hero:** las frases que se escriben solas están en `data-typed`, separadas por `|`.
- **Iconos:** sprite SVG inline al inicio del `<body>`; se usan con `<svg class="icon"><use href="#i-nombre"/></svg>`.

## Características

- Diseño oscuro y responsive, con menú móvil a pantalla completa.
- Accesibilidad: enlace "Saltar al contenido", estados `aria-expanded` y `aria-pressed`, foco visible, contraste AA para texto secundario y respeto de `prefers-reduced-motion`.
- Funciona sin JavaScript: el contenido sigue visible.
- SEO: metadatos, Open Graph, Twitter Card y datos estructurados (`Person`, JSON-LD).
- Fuentes desde Google Fonts (Manrope, IBM Plex Sans, IBM Plex Mono); el resto es local.

## Pendiente

- Añadir `og:image` (1200×630) y `canonical` cuando esté definida la URL final.
- Enlaces a demo o repositorio en las tarjetas de proyectos.
- CV descargable.

## Contacto

- Email: mike.mavc27@gmail.com
- GitHub: https://github.com/MikeRider27
- LinkedIn: https://www.linkedin.com/in/miguel-villalba-673517181/

## Autor
Miguel Villalba, 2026

## Licencia

MIT License. Puedes usar este portafolio como plantilla para tu propio sitio personal, pero no reutilices mi foto, mis textos, mi experiencia ni mis datos de contacto: reemplázalos por los tuyos. Consulta el archivo [LICENSE](LICENSE) para más detalles.

