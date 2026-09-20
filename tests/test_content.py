import copy
import csv
import importlib.util
import json
import re
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('builder', ROOT/'scripts/build_content.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ContentTests(unittest.TestCase):
    def test_native_text_has_no_damaged_characters_inside_words(self):
        for lang in ('qu', 'ay'):
            for key, value in self.locales[lang]['messages'].items():
                self.assertNotIn('\ufffd', value, f'{lang}/{key}')
                self.assertIsNone(re.search(r'\w\?\w', value), f'{lang}/{key}: {value}')

    def setUp(self):
        self.catalog, self.locales = builder.load()

    def test_complete_content_and_generated_bundle(self):
        builder.validate(self.catalog,self.locales)
        self.assertEqual(sum(a['showCard'] for a in self.catalog['articles']),9)
        for article in self.catalog['articles']:
            if article['showCard']:
                self.assertTrue(article['activity'])
        bundle=(ROOT/'assets/content.js').read_text(encoding='utf-8')
        payload=json.loads(bundle.split('window.QAS_CONTENT = ',1)[1].removesuffix(';\n'))
        self.assertEqual(payload,{'catalog':self.catalog,'locales':self.locales})

    def test_missing_key_is_rejected(self):
        del self.locales['en']['messages']['article.moon.title']
        with self.assertRaises(AssertionError): builder.validate(self.catalog,self.locales)

    def test_all_four_languages_have_complete_text(self):
        for lang, locale in self.locales.items():
            for key, value in locale['messages'].items():
                self.assertIsInstance(value, str, f'{lang}/{key}')
                self.assertTrue(value.strip(), f'{lang}/{key}')
            self.assertTrue((ROOT/f'contenido/lectura-{lang}.md').exists())

    def test_native_translations_are_explicit_drafts_and_keep_names(self):
        for lang in ('qu','ay'):
            locale=self.locales[lang]
            self.assertEqual(locale['meta']['status'],'draft')
            self.assertTrue(locale['meta']['needsReview'])
            self.assertIsNone(locale['meta']['reviewer'])
            messages=locale['messages']
            for name in ('QAS','Quechua Aimara Space','Puno','Perú'):
                self.assertIn(name,messages['article.mission.p1'])
            for name in ('Mercurio','Venus','Tierra','Marte','Júpiter','Saturno','Urano','Neptuno'):
                self.assertIn(name,messages['article.planets.p2'])
            self.assertIn('Vía Láctea',messages['article.stars.p2'])
            for key in ('article.sun.p4','article.moon.p3','article.earth.p4'):
                self.assertNotEqual(messages[key],self.locales['es']['messages'][key])

    def test_html_in_translation_is_rejected(self):
        self.locales['qu']['messages']['ui.home']='<img src=x onerror=alert(1)>'
        with self.assertRaises(AssertionError): builder.validate(self.catalog,self.locales)

    def test_csv_round_trip_preserves_accents_and_multiline(self):
        original=copy.deepcopy(self.locales)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'translation.csv'
            with (ROOT/'contenido/traducciones.csv').open(encoding='utf-8-sig',newline='') as handle:
                rows=list(csv.DictReader(handle))
            for row in rows:
                if row['id']=='ui.home': row['qu']='Prueba: á, ñ\nSegunda línea'
            with path.open('w',encoding='utf-8-sig',newline='') as handle:
                writer=csv.DictWriter(handle,fieldnames=['id','es','en','qu','ay'])
                writer.writeheader();writer.writerows(rows)
            builder.import_csv(path,self.locales)
        self.assertEqual(self.locales['qu']['messages']['ui.home'],'Prueba: á, ñ\nSegunda línea')
        self.assertEqual(original['es'],self.locales['es'])
        self.assertEqual(original['en'],self.locales['en'])
        builder.validate(self.catalog,self.locales)

    def test_duplicate_csv_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'duplicate.csv'
            with (ROOT/'contenido/traducciones.csv').open(encoding='utf-8-sig',newline='') as handle:
                rows=list(csv.DictReader(handle))
            rows[-1]['id']=rows[0]['id']
            with path.open('w',encoding='utf-8-sig',newline='') as handle:
                writer=csv.DictWriter(handle,fieldnames=['id','es','en','qu','ay'])
                writer.writeheader();writer.writerows(rows)
            with self.assertRaises(AssertionError): builder.import_csv(path,self.locales)


if __name__=='__main__': unittest.main()
