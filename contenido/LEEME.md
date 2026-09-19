# Contenido y traducciones de QAS

La base contiene nueve temas educativos, diez definiciones, la presentación de QAS y las fuentes. Cada tema tiene una explicación breve. Los temas educativos incluyen una actividad; el glosario también tiene una propuesta de trabajo.

La página ahora se genera como HTML estático por idioma y artículo. Consulta `../PUBLICAR-Y-BUSCADORES.md` para publicar y configurar Search Console. La portada se edita en `templates/home.html`; `index.html` y los archivos de `es/`, `en/`, `qu/` y `ay/` se generan automáticamente.

## Revisar el contenido

- `lectura-es.md`: todos los artículos en español, con actividades y fuentes.
- `lectura-en.md`: versión en inglés.
- `lectura-qu.md`: borrador completo en quechua sureño, con referencia Cusco-Collao.
- `lectura-ay.md`: borrador completo en aimara del sur del Perú, con referencia Puno.
- `traducciones.csv`: tabla con una fila por texto y columnas `id`, `es`, `en`, `qu`, `ay`. Se puede abrir en Excel o LibreOffice como CSV UTF-8 separado por comas.

Los documentos de lectura y la tabla se generan desde los archivos JSON. No edites los documentos de lectura para cambiar la página.

## Traducir mediante la tabla

1. Guarda una copia de `traducciones.csv` con otro nombre, por ejemplo `revision-quechua.csv`.
2. Mantén la columna `id` y los encabezados. Traduce en la columna del idioma correspondiente. Conserva todas las filas y las otras columnas. Las celdas vacías de quechua y aimara indican traducciones pendientes.
3. Guarda como CSV UTF-8, separado por comas. Conserva los acentos y los saltos de línea que Excel pueda guardar entre comillas.
4. Desde la carpeta del proyecto, ejecuta:

   ```powershell
   python scripts/build_content.py --import-csv contenido/revision-quechua.csv
   ```

5. Abre o recarga `index.html` y selecciona el idioma. No hace falta un servidor ni instalar paquetes de Python.

La importación sustituye los textos de las cuatro columnas. Usa una copia reciente para evitar sobrescribir cambios de otra persona. El programa valida todo antes de escribir. Ejecutar el programa sin `--import-csv` vuelve a generar la tabla desde los JSON; por eso conviene trabajar sobre una copia con otro nombre.

## Editar directamente

- `idiomas/es.json`: contenido original en español.
- `idiomas/en.json`: traducción al inglés, pendiente de revisión editorial.
- `idiomas/qu.json` y `idiomas/ay.json`: traducciones completas de interfaz, artículos, actividades, glosario, fuentes y descargas. Son borradores generados con ayuda de IA, sin validación de hablantes locales.
- `catalogo.json`: orden de temas, categorías, identificadores de párrafos y fuentes. Los enlaces y la estructura no se traducen.

Cada archivo de idioma tiene `meta` para registrar `variant` (variante lingüística), `reviewer` (persona revisora) y `status` (`base`, `draft`, `pending` o `reviewed`). Estos datos documentan el trabajo; no reemplazan una revisión real ni bloquean automáticamente la publicación de los textos introducidos.

Los borradores en quechua y aimara tienen además `needsReview: true` y `translationMethod`. La página, los documentos de lectura y las guías descargadas muestran una nota en el idioma correspondiente. Una vez realizada la revisión lingüística, registra la persona revisora y cambia `needsReview` a `false`; no marques como revisado un texto que no haya sido revisado.

Después de editar los JSON, ejecuta:

```powershell
python scripts/build_content.py
```

Esto actualiza `assets/content.js`, la tabla, los cuatro documentos de lectura y las páginas HTML. No edites los archivos generados a mano. Puedes abrir las páginas directamente desde el explorador de archivos. Los artículos también funcionan sin JavaScript.

## Criterios de escritura y traducción

- Una idea principal por párrafo. Usa frases cortas y palabras habituales.
- Explica un término científico la primera vez que aparece. Consulta el glosario para mantener el mismo significado en toda la página.
- Traduce frases completas. No unas fragmentos suponiendo que todas las lenguas tienen el mismo orden de palabras.
- Escribe solo texto: sin HTML, etiquetas ni código. El diseño vive en otros archivos.
- Conserva las unidades y el sentido de las cantidades aproximadas.
- Si no hay una palabra equivalente de uso común, acuerda una explicación con hablantes de la variante elegida.
- No presentes un relato de una comunidad como una creencia compartida por todos los pueblos andinos. Registra procedencia, permiso de publicación y forma de atribución antes de añadir relatos o grabaciones.
- No inventes una traducción para llenar una celda. Deja `null` o la celda vacía hasta resolverla.

## Cobertura y revisión

La página usa español cuando falta una traducción y muestra un aviso. Cada fragmento mantiene la etiqueta de idioma correspondiente para lectores de pantalla. No aparecen identificadores técnicos ni espacios vacíos. Una descarga completamente en español se identifica como `QAS-guia-es.txt`, aunque se haya seleccionado una lengua pendiente.

Los cuatro idiomas tienen todas las unidades traducidas. Quechua y aimara requieren revisión lingüística y adaptación a la comunidad destinataria. La cobertura completa indica que no faltan textos; no equivale a una validación de la gramática o la terminología.

Se conservan marcas, instituciones, lugares y nombres propios: QAS, Quechua Aimara Space, NASA, Reniec, Minedu, Ministerio de Educación, Puno, Perú, Unsplash y Vía Láctea. En quechua y aimara se conservan los nombres de los planetas de la lista original. Los conceptos comunes —Sol, Luna, estrella— se traducen. Los préstamos científicos se explican en contexto y necesitan revisión terminológica; no se presentan como términos normalizados.

Para el vocabulario se consultaron el [Vocabulario pedagógico aimara de Minedu](https://formacionenservicio.minedu.gob.pe/sifods/centro-recurso/2022/Material-educativo/Libro/vocabulario-pedagogico-aimara.pdf) y la [Biblioteca Quechua Sureño de Minedu](https://www.gob.pe/institucion/minedu/informes-publicaciones/4548552-biblioteca-quechua-sureno). Estas referencias no validan las traducciones de QAS ni implican aval institucional.

## Añadir un tema

Agrega una entrada en `catalogo.json` con un identificador único, categoría, símbolo, lista de párrafos y fuentes. Crea sus claves `article.identificador.title`, `article.identificador.summary`, párrafos y actividad en los cuatro archivos de idioma. Usa `null` en traducciones pendientes. No renombres claves ya traducidas si el concepto sigue siendo el mismo.

Registra también sus cuatro nombres de archivo en `SLUGS` dentro de `scripts/site_generator.py`. Conserva las direcciones de artículos existentes; cambiarlas después de publicar requiere redirecciones para no perder enlaces.

## Comprobaciones

```powershell
python scripts/build_content.py
python -m unittest discover -s tests
```

El contenido científico enlaza recursos de NASA; el vocabulario de la portada enlaza Reniec y Minedu. Las actividades de aula y observación son propuestas didácticas de QAS, no actividades atribuidas a una comunidad determinada.
