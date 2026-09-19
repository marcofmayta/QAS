"""Validate QAS content and generate the local-file-compatible browser bundle.

Usage: python scripts/build_content.py
       python scripts/build_content.py --import-csv contenido/traducciones.csv
Only the Python standard library is required.
"""
import argparse
import csv
import json
from pathlib import Path
import re
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from site_generator import generate_site, normalize_site_url

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ('es', 'en', 'qu', 'ay')

def load():
    catalog = json.loads((ROOT/'contenido/catalogo.json').read_text(encoding='utf-8'))
    locales = {lang: json.loads((ROOT/f'contenido/idiomas/{lang}.json').read_text(encoding='utf-8')) for lang in LANGUAGES}
    return catalog, locales

def validate(catalog, locales):
    base = locales['es']['messages']
    assert base, 'El contenido base está vacío.'
    for lang, document in locales.items():
        assert document['meta']['code'] == lang, f'Código de idioma incorrecto: {lang}'
        assert set(document['messages']) == set(base), f'Claves diferentes en {lang}'
        for key, value in document['messages'].items():
            assert value is None or isinstance(value,str), f'Texto inválido: {lang}/{key}'
            if lang in ('es','en'):
                assert value and value.strip(), f'Traducción vacía: {lang}/{key}'
            if value:
                assert not re.search(r'<[^>]+>',value), f'No usar HTML: {lang}/{key}'
    ids = [article['id'] for article in catalog['articles']]
    assert len(ids)==len(set(ids)), 'Identificadores de artículos duplicados'
    for article in catalog['articles']:
        assert article['category'] in ('solar','astronomy','andino','learning')
        keys = [f'article.{article["id"]}.title', *article['paragraphs']]
        if article['showCard']: keys.append(f'article.{article["id"]}.summary')
        if article.get('activity'): keys.append(article['activity'])
        assert all(key in base for key in keys), f'Contenido incompleto: {article["id"]}'
        assert all(source in catalog['sources'] for source in article['sources'])
    for term in catalog['glossary']:
        assert f'glossary.{term}.term' in base and f'glossary.{term}.definition' in base
    page = (ROOT/'templates/home.html').read_text(encoding='utf-8')
    for key in re.findall(r'data-i18n(?:-aria)?="([^"]+)"',page):
        assert key in base, f'Clave ausente en HTML: {key}'
    for source in catalog['sources'].values():
        assert source['url'].startswith('https://'), 'Las fuentes deben usar HTTPS'
        assert source['labelKey'] in base, 'Falta traducir el nombre de una fuente'

def import_csv(path, locales):
    with Path(path).open(encoding='utf-8-sig',newline='') as handle:
        reader=csv.DictReader(handle)
        assert reader.fieldnames == ['id',*LANGUAGES], 'Se requieren las columnas id, es, en, qu, ay.'
        rows=list(reader)
    assert len(rows)==len(locales['es']['messages']), 'La tabla debe incluir todas las filas.'
    assert len({row['id'] for row in rows})==len(rows), 'Hay identificadores repetidos.'
    assert {row['id'] for row in rows}==set(locales['es']['messages']), 'No modificar los identificadores.'
    for row in rows:
        for lang in LANGUAGES:
            assert row[lang] is not None, 'Fila CSV incompleta.'
            locales[lang]['messages'][row['id']]=row[lang].strip() or None

def generate(catalog,locales):
    assets=ROOT/'assets';assets.mkdir(exist_ok=True)
    data=json.dumps({'catalog':catalog,'locales':locales},ensure_ascii=False,indent=2)
    (assets/'content.js').write_text('// Generado por scripts/build_content.py. Editar contenido/idiomas/*.json.\nwindow.QAS_CONTENT = '+data+';\n',encoding='utf-8')
    with (ROOT/'contenido/traducciones.csv').open('w',encoding='utf-8-sig',newline='') as handle:
        writer=csv.writer(handle)
        writer.writerow(['id',*LANGUAGES])
        for key in locales['es']['messages']:
            writer.writerow([key,*[locales[lang]['messages'][key] or '' for lang in LANGUAGES]])
    for lang in LANGUAGES:
        # Future partial translations still produce a readable review document.
        m={key: value or locales['es']['messages'][key] for key,value in locales[lang]['messages'].items()}
        lines=['# QAS · Quechua Aimara Space','',m['ui.heroDescription'],'']
        if locales[lang]['meta'].get('needsReview'):
            lines.extend([m['ui.translationDraft'],''])
        if any(not value for value in locales[lang]['messages'].values()):
            lines.extend([m['ui.pendingTranslation'],''])
        for article in catalog['articles']:
            key=article['id']
            lines.extend(['## '+m[f'article.{key}.title'],''])
            for paragraph in article['paragraphs']: lines.extend([m[paragraph],''])
            if key=='glossary':
                for term in catalog['glossary']:
                    lines.extend(['**'+m[f'glossary.{term}.term']+'**: '+m[f'glossary.{term}.definition'],''])
            if article.get('activity'): lines.extend(['### '+m['ui.activity'],'',m[article['activity']],''])
            if article['sources']:
                lines.extend(['### '+m['ui.sourceHeading'],''])
                for source_id in article['sources']:
                    source=catalog['sources'][source_id]
                    lines.append(f'- [{m[source["labelKey"]]}]({source["url"]})')
                lines.append('')
        (ROOT/f'contenido/lectura-{lang}.md').write_text('\n'.join(lines),encoding='utf-8')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-csv',type=Path)
    parser.add_argument('--site-url',help='URL pública HTTPS, incluida la carpeta del proyecto si existe.')
    parser.add_argument('--google-verification',help='Solo el valor content de la etiqueta de Search Console.')
    parser.add_argument('--bing-verification',help='Solo el valor content de la etiqueta de Bing Webmaster Tools.')
    args=parser.parse_args()
    catalog,locales=load()
    if args.import_csv: import_csv(args.import_csv,locales)
    validate(catalog,locales)
    config=json.loads((ROOT/'site-config.json').read_text(encoding='utf-8'))
    if args.site_url is not None: config['siteUrl']=normalize_site_url(args.site_url)
    if args.google_verification is not None: config['googleVerification']=args.google_verification
    if args.bing_verification is not None: config['bingVerification']=args.bing_verification
    normalize_site_url(config.get('siteUrl'))
    if args.import_csv:
        for lang,document in locales.items():
            (ROOT/f'contenido/idiomas/{lang}.json').write_text(json.dumps(document,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    generate(catalog,locales)
    manifest=generate_site(ROOT,catalog,locales,config)
    (ROOT/'site-config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    cards=sum(article['showCard'] for article in catalog['articles'])
    print(f'OK: {cards} temas, {len(catalog["glossary"])} definiciones, {len(locales["es"]["messages"])} unidades por idioma.')
    print(f'HTML: {manifest["canonicalPages"]} páginas por idioma/artículo, más portada de entrada.')
    if manifest['requiresSiteUrl']: print('Falta la URL pública: sitemap y etiquetas canónicas se generarán con --site-url.')

if __name__=='__main__': main()
