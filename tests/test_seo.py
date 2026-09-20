import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('seo',ROOT/'scripts/site_generator.py')
seo=importlib.util.module_from_spec(spec);spec.loader.exec_module(seo)

class SeoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=json.loads((ROOT/'contenido/catalogo.json').read_text(encoding='utf-8'))
        cls.locales={lang:json.loads((ROOT/f'contenido/idiomas/{lang}.json').read_text(encoding='utf-8')) for lang in seo.LANGUAGES}

    def nodes(self,path):return list(seo.parse(path.read_text(encoding='utf-8')).walk())

    def test_article_text_and_language_links_exist_without_javascript(self):
        for lang in seo.LANGUAGES:
            for article in self.catalog['articles']:
                path=ROOT/seo.page_path(lang,article['id'])
                text=path.read_text(encoding='utf-8');nodes=self.nodes(path)
                self.assertEqual(next(n for n in nodes if n.tag=='html').attrs['lang'],lang)
                self.assertEqual(len([n for n in nodes if n.tag=='h1']),1)
                for key in article['paragraphs']:
                    self.assertIn(seo.escape(self.locales[lang]['messages'][key],quote=False),text)
                self.assertEqual(len([n for n in nodes if n.tag=='a' and n.attrs.get('hreflang')]),4)
                for node in nodes:
                    if node.tag=='script':
                        self.assertTrue(node.attrs.get('type') in ('application/ld+json','application/json') or node.attrs.get('src')=='../assets/share.js')

    def test_homes_have_static_cards_and_valid_local_links(self):
        manifest=json.loads((ROOT/'site-manifest.json').read_text(encoding='utf-8'))
        for path in [ROOT/'index.html',*[ROOT/seo.page_path(code) for code in seo.LANGUAGES]]:
            nodes=self.nodes(path)
            self.assertEqual(len([n for n in nodes if n.attrs.get('class')=='card']),9)
            self.assertFalse(any(n.tag=='button' and 'data-article' in n.attrs for n in nodes))
        for filename in manifest['files']:
            if not filename.endswith('.html'):continue
            path=ROOT/filename
            for node in self.nodes(path):
                for attribute in ('href','src'):
                    value=node.attrs.get(attribute,'') or ''
                    if not value or value.startswith('#') or urlsplit(value).scheme:continue
                    target=(path.parent/urlsplit(value).path).resolve()
                    self.assertTrue(target.is_relative_to(ROOT))
                    self.assertTrue(target.exists(),f'{filename}: {value}')

    def test_github_subpath_sitemap_and_reciprocal_canonicals(self):
        base='https://example.github.io/qas/'
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)
            config={'siteUrl':base,'googleVerification':'sample-token','bingVerification':'sample-bing'}
            manifest=seo.generate_site(ROOT,self.catalog,self.locales,config,out)
            tree=ET.parse(out/'sitemap.xml')
            urls=[node.text for node in tree.findall('.//{*}loc')]
            self.assertEqual(len(urls),48);self.assertEqual(len(set(urls)),48)
            self.assertIn(base+'es/la-luna.html',urls)
            self.assertIn('Sitemap: '+base+'sitemap.xml',(out/'robots.txt').read_text())
            for lang in seo.LANGUAGES:
                for article in [None,*[a['id'] for a in self.catalog['articles']]]:
                    path=seo.page_path(lang,article);nodes=self.nodes(out/path)
                    canonical=next(n for n in nodes if n.attrs.get('rel')=='canonical')
                    self.assertEqual(canonical.attrs['href'],base+path)
                    alternates=[n for n in nodes if n.attrs.get('rel')=='alternate']
                    self.assertEqual(len(alternates),5)
                    self.assertEqual({n.attrs['href'] for n in alternates},{base+seo.page_path(code,article) for code in seo.LANGUAGES})
            nodes=self.nodes(out/'index.html')
            self.assertEqual(next(n for n in nodes if n.attrs.get('name')=='google-site-verification').attrs['content'],'sample-token')
            self.assertFalse(manifest['requiresSiteUrl'])

    def test_unknown_domain_does_not_generate_fake_urls(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)
            manifest=seo.generate_site(ROOT,self.catalog,self.locales,{'siteUrl':None},out)
            self.assertFalse((out/'sitemap.xml').exists())
            self.assertTrue(manifest['requiresSiteUrl'])
            self.assertFalse(any(n.attrs.get('rel')=='canonical' for n in self.nodes(out/'index.html')))

    def test_url_validation(self):
        self.assertEqual(seo.normalize_site_url('https://example.org/qas'),'https://example.org/qas/')
        for value in ('file:///tmp/site','https://user:password@example.org/','https://example.org/?secret=x','https://example.org/index.html'):
            with self.assertRaises(ValueError):seo.normalize_site_url(value)

if __name__=='__main__':unittest.main()
