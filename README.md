# QAS · Quechua Aimara Space

**Un mismo cielo. Muchas voces.**

[Visita QAS](https://marcofmayta.github.io/QAS/)

QAS es un proyecto educativo que acerca la astronomía a estudiantes, familias y comunidades de Puno y del Perú, con contenidos en español, inglés, quechua y aimara. Combina explicaciones sencillas sobre el espacio, vocabulario y actividades para aprender en la escuela, en casa o en comunidad.

Nace del interés por compartir ciencia en nuestras lenguas y crear un espacio donde la curiosidad por el universo pueda expresarse desde distintos contextos culturales.

## Propósito

- Facilitar el acceso a conceptos de astronomía en cuatro lenguas.
- Ofrecer actividades con materiales cotidianos y propuestas de observación sin telescopio.
- Valorar las lenguas originarias y promover la participación de sus hablantes en la creación y revisión de contenidos.
- Conectar el aprendizaje científico con las preguntas y experiencias de las comunidades.

QAS reconoce que cada comunidad tiene sus propias voces y formas de transmitir conocimientos. La incorporación de relatos, palabras o grabaciones debe respetar su procedencia, atribución y autorización para compartirlos.

## Qué puedes encontrar

La versión piloto incluye nueve temas educativos, con explicaciones y actividades:

| Tema | Qué se aprende |
| --- | --- |
| Las estrellas y las galaxias | Estrellas, Vía Láctea y nebulosas. |
| El sistema solar | El Sol, los planetas y otros cuerpos que lo integran. |
| Las lenguas y el cielo | Palabras en quechua y aimara y aprendizaje en comunidad. |
| El Sol | Su energía, su luz y la observación de sombras. |
| La Luna y sus fases | Por qué cambia la parte iluminada que vemos. |
| La Tierra | Rotación, día y noche, traslación y estaciones. |
| Observación del cielo | Cómo preparar y registrar una observación. |
| Glosario | Diez definiciones de conceptos astronómicos. |
| Actividad para la escuela | Un modelo de las fases lunares con una pelota y una linterna. |

También incluye una presentación del proyecto, referencias para seguir aprendiendo y una guía de observación descargable en formato de texto, con campos para registrar fecha, lugar, condiciones del cielo y descubrimientos.

## Idiomas y revisión

| Idioma | Estado actual |
| --- | --- |
| Español | Contenido base completo. |
| Inglés | Traducción completa, pendiente de revisión editorial. |
| Quechua | Borrador completo; referencia quechua sureño, Cusco-Collao. |
| Aimara | Borrador completo; referencia aimara del sur del Perú, Puno. |

**Las traducciones al quechua y al aimara se generaron con ayuda de IA y todavía requieren revisión por hablantes locales.** Tener todos los textos traducidos no equivale a una validación lingüística. La adaptación a las variantes de las comunidades destinatarias es una prioridad del proyecto.

Se conservan los nombres propios y las denominaciones institucionales. Los conceptos comunes se traducen y los términos científicos se explican en contexto. Cuando falta una traducción, el sistema utiliza el texto en español.

## Experiencia de uso

- Diseño adaptable a celulares, tabletas y computadoras.
- Navegación por idioma y filtros por categoría.
- Lectura de artículos en una ventana dentro de la portada o en una página independiente.
- Artículos y enlaces entre idiomas disponibles sin JavaScript.
- Ilustraciones del espacio y animaciones suaves, con un control para pausarlas y respeto por la preferencia de movimiento reducido del dispositivo.
- Guía de observación descargable en el idioma seleccionado.
- Sección de contacto y convocatoria de voluntarios.

Las ilustraciones son recursos educativos; el sitio no muestra un mapa del cielo en tiempo real. La fotografía de montaña es referencial y no se identifica como una fotografía de Puno.

## Cómo está construido

QAS es un sitio estático desarrollado con **HTML, CSS y JavaScript**, con scripts de **Python** para validar el contenido y generar las páginas. No necesita una base de datos ni un servidor de aplicación. Los scripts utilizan la biblioteca estándar de Python.

El contenido está separado del diseño: los textos se guardan en archivos JSON por idioma y también se exportan a una tabla CSV para facilitar la revisión por personas traductoras. Actualmente hay 183 unidades de texto por idioma y 48 páginas por idioma y artículo, además de la portada de entrada.

| Ruta | Función |
| --- | --- |
| `contenido/idiomas/` | Textos y metadatos de revisión de los cuatro idiomas. |
| `contenido/catalogo.json` | Organización de artículos, categorías, glosario y fuentes. |
| `contenido/traducciones.csv` | Tabla generada para trabajar en las traducciones. |
| `contenido/lectura-*.md` | Documentos generados para revisar los artículos de cada idioma. |
| `templates/home.html` | Plantilla de la portada. |
| `assets/` | Estilos, interacciones, animaciones y contenido generado para el navegador. |
| `scripts/` | Validación, generación de páginas y preparación del paquete del sitio. |
| `es/`, `en/`, `qu/`, `ay/` | Páginas HTML generadas por idioma. |
| `tests/` | Pruebas de contenido, enlaces, generación e interfaz. |
| `index.html` | Portada de entrada generada. |

Para explorar la versión local, abre `index.html` en un navegador. Para modificar el proyecto, edita los archivos fuente y regenera las páginas:

```bash
python scripts/build_content.py
```

Las comprobaciones automatizadas de Python se ejecutan con:

```bash
python -m unittest discover -s tests
```

Los archivos HTML generados, `assets/content.js` y los documentos de lectura se sobrescriben al regenerar. La [guía de contenido y traducciones](contenido/LEEME.md) explica cómo editar los JSON, importar una revisión en CSV y añadir temas.

## Fuentes y enfoque educativo

Los artículos enlazan recursos educativos de NASA para los conceptos de astronomía. El vocabulario toma como referencia materiales de Reniec y del Ministerio de Educación del Perú. Las referencias concretas se encuentran en cada artículo y en `contenido/catalogo.json`.

Las actividades son propuestas didácticas de QAS. El uso de estas fuentes no implica respaldo institucional al proyecto ni validación de sus traducciones.

## Colabora con QAS

Buscamos personas que quieran aportar en:

- **Idiomas:** revisión de quechua y aimara, adaptación local y revisión del inglés.
- **Educación y astronomía:** revisión científica, actividades y materiales para el aula.
- **Diseño:** ilustración, accesibilidad y experiencia de lectura.
- **Marketing y comunicación:** difusión y contacto con comunidades educativas.
- **Programación:** mejoras de la interfaz, herramientas de contenido y pruebas.

Las próximas prioridades son revisar las traducciones con hablantes locales, recoger comentarios de estudiantes y docentes, y mejorar los materiales a partir de su uso en las comunidades.

## Contacto

El proyecto es impulsado por un estudiante de doctorado del ICMC–USP, ingeniero estadístico e informático por la UNA Puno, investigador RENACYT y quechuahablante.

Para colaborar o conversar sobre QAS, puedes [contactarme por LinkedIn](https://www.linkedin.com/in/marco-mayta-835781170/).
