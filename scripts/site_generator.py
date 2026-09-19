"""Generate crawlable QAS pages using only the Python standard library."""
from html import escape
from html.parser import HTMLParser
import json
import posixpath
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import xml.etree.ElementTree as ET

LANGUAGES = ('es', 'en', 'qu', 'ay')
NAMES = {'es':'Español', 'en':'English', 'qu':'Quechua', 'ay':'Aimara'}
SLUGS = {
    'stars': ('estrellas-galaxias','stars-galaxies','quyllurkuna','wara-waranaka'),
    'planets': ('sistema-solar','solar-system','intiwan-muyuqmasinkuna','willka-muyuri-masinaka'),
    'andes': ('lenguas-y-cielo','languages-and-sky','simikuna-hanaq-pacha','arunaka-alaxpacha'),
    'mission': ('sobre-qas','about-qas','qas-manta','qas-tuqi'),
    'sources': ('fuentes','sources','pukyukuna','yatiyi-utjirinaka'),
    'sun': ('el-sol','the-sun','inti','willka'),
    'moon': ('la-luna','the-moon','killa','phaxsi'),
    'earth': ('la-tierra','earth','kay-pacha','uraqi'),
    'observe': ('observar-el-cielo','skywatching','hanaq-pachata-qhaway','alaxpacha-unjana'),
    'glossary': ('glosario','glossary','simi-pirwa','aru-pirwa'),
    'classroom': ('actividad-escolar','classroom-activity','yachaywasi-ruray','yatiqana-lurawi'),
}
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

class Node:
    def __init__(self,tag=None,attrs=None,children=None):
        self.tag,self.attrs,self.children=tag,dict(attrs or {}),list(children or [])
    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child,Node): yield from child.walk()
    def find(self,predicate):
        return next(node for node in self.walk() if predicate(node))
    def html(self):
        content=''.join(child.html() if isinstance(child,Node) else child if self.tag in ('script','style') else escape(child,quote=False) for child in self.children)
        if not self.tag:return content
        attrs=''.join(' '+key+('' if value is None else '="'+escape(str(value),quote=True)+'"') for key,value in self.attrs.items())
        if self.tag in VOID:return '<'+self.tag+attrs+'>'
        return '<'+self.tag+attrs+'>'+content+'</'+self.tag+'>'

class TreeParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root=Node();self.stack=[self.root]
    def handle_starttag(self,tag,attrs):
        node=Node(tag,attrs);self.stack[-1].children.append(node)
        if tag not in VOID:self.stack.append(node)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.stack.pop()
    def handle_endtag(self,tag):
        for index in range(len(self.stack)-1,0,-1):
            if self.stack[index].tag==tag:
                self.stack=self.stack[:index];return
    def handle_data(self,data):self.stack[-1].children.append(data)

def parse(text):
    parser=TreeParser();parser.feed(text);return parser.root

def normalize_site_url(value):
    if not value:return None
    url=urlsplit(value.strip())
    if url.scheme!='https' or not url.hostname or url.username or url.password or url.query or url.fragment:
        raise ValueError('siteUrl debe ser la URL HTTPS pública del sitio, sin usuario, consulta ni fragmento.')
    if any(part in ('.','..') for part in url.path.split('/')) or url.path.endswith('.html'):
        raise ValueError('Indica la carpeta base pública, no una página HTML.')
    return urlunsplit((url.scheme,url.netloc,url.path.rstrip('/')+'/', '', ''))

def page_path(lang,article=None):
    return f'{lang}/'+(SLUGS[article][LANGUAGES.index(lang)]+'.html' if article else 'index.html')

def relative(current,target):return posixpath.relpath(target,posixpath.dirname(current) or '.')

def text_for(locales,lang,key):return locales[lang]['messages'].get(key) or locales['es']['messages'][key]

def translated(locales,lang,key,tag='p',attrs=None):
    actual=lang if locales[lang]['messages'].get(key) else 'es'
    return Node(tag,{**(attrs or {}),'lang':actual},[text_for(locales,lang,key)])

def language_links(lang,current,article=None,label='Languages'):
    return Node('nav',{'class':'language-links','aria-label':label},[
        Node('a',{'href':relative(current,page_path(code,article)),'hreflang':code,'lang':code,
                  **({'aria-current':'page'} if code==lang else {})},[NAMES[code]]) for code in LANGUAGES])

def metadata(lang,article_id,title,description,config):
    base=normalize_site_url(config.get('siteUrl'))
    nodes=[Node('meta',{'name':'description','content':description}),
           Node('meta',{'name':'robots','content':'index, follow, max-image-preview:large'}),
           Node('meta',{'property':'og:title','content':title}),
           Node('meta',{'property':'og:description','content':description}),
           Node('meta',{'property':'og:type','content':'article' if article_id else 'website'}),
           Node('meta',{'property':'og:site_name','content':'QAS · Quechua Aimara Space'})]
    schema={'@context':'https://schema.org','@type':'Article' if article_id else 'WebSite',
            'name':title,'description':description,'inLanguage':lang}
    if article_id:schema['headline']=title
    if base:
        url=base+page_path(lang,article_id)
        nodes.extend([Node('link',{'rel':'canonical','href':url}),Node('meta',{'property':'og:url','content':url})])
        for code in LANGUAGES:
            nodes.append(Node('link',{'rel':'alternate','hreflang':code,'href':base+page_path(code,article_id)}))
        nodes.append(Node('link',{'rel':'alternate','hreflang':'x-default','href':base+page_path('es',article_id)}))
        schema['url']=url
    for key,name in [('googleVerification','google-site-verification'),('bingVerification','msvalidate.01')]:
        if config.get(key):nodes.append(Node('meta',{'name':name,'content':config[key]}))
    nodes.append(Node('script',{'type':'application/ld+json'},[json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')]))
    return nodes

def article_body(catalog,locales,lang,article):
    children=[translated(locales,lang,key) for key in article['paragraphs']]
    if article['id']=='glossary':
        definitions=[]
        for term in catalog['glossary']:
            definitions.extend([translated(locales,lang,f'glossary.{term}.term','dt'),translated(locales,lang,f'glossary.{term}.definition','dd')])
        children.append(Node('dl',{'class':'glossary'},definitions))
    if article.get('activity'):
        children.append(Node('section',{'class':'article-activity'},[
            translated(locales,lang,'ui.activity','h2'),translated(locales,lang,article['activity'])]))
    if article['sources']:
        children.append(translated(locales,lang,'ui.sourceHeading','h2'))
        links=[]
        for source_id in article['sources']:
            source=catalog['sources'][source_id]
            links.append(Node('li',children=[translated(locales,lang,source['labelKey'],'a',{'href':source['url'],'target':'_blank','rel':'noopener noreferrer'})]))
        children.append(Node('ul',{'class':'source'},links))
    return children

def render_card(catalog,locales,lang,current,article):
    key=article['id'];category={'astronomy':'astronomyTag','solar':'solarTag','andino':'andinoTag','learning':'learningTag'}[article['category']]
    scene=Node('div',{'class':'scene','aria-hidden':'true'},[Node('span',{'class':c}) for c in ('scene-orbit','scene-orbit outer','scene-body','scene-mountain')])
    visual=Node('div',{'class':'card-image topic-art topic-'+key},[
        Node('span',{'class':'topic-symbol','aria-hidden':'true'},[article['symbol']]),translated(locales,lang,'ui.'+category,'span',{'class':'tag'}),scene])
    link=translated(locales,lang,'ui.readArticle','a',{'class':'small-link','data-article':key,'href':relative(current,page_path(lang,key)),'aria-describedby':'card-'+key})
    link.children.append(Node('span',{'aria-hidden':'true'},['↗']))
    body=Node('div',{'class':'card-body'},[
        translated(locales,lang,f'article.{key}.title','h3',{'id':'card-'+key}),
        translated(locales,lang,f'article.{key}.summary'),link])
    return Node('article',{'class':'card','data-category':article['category']},[visual,body])

def render_home(template,catalog,locales,lang,current,config):
    root=parse(template)
    root.find(lambda n:n.tag=='html').attrs['lang']=lang
    for node in list(root.walk()):
        if 'data-i18n' in node.attrs:
            key=node.attrs['data-i18n'];node.children=[text_for(locales,lang,key)]
            node.attrs['lang']=lang if locales[lang]['messages'].get(key) else 'es'
        if 'data-i18n-aria' in node.attrs:node.attrs['aria-label']=text_for(locales,lang,node.attrs['data-i18n-aria'])
        for attr in ('href','src'):
            value=node.attrs.get(attr,'')
            if value.startswith('assets/'):node.attrs[attr]=relative(current,value)
        if node.tag=='button' and 'data-article' in node.attrs:
            node.tag='a';node.attrs['href']=relative(current,page_path(lang,node.attrs['data-article']))
        if node.tag=='option':
            if node.attrs.get('value')==lang:node.attrs['selected']=None
            else:node.attrs.pop('selected',None)
    head=root.find(lambda n:n.tag=='head')
    head.children=[n for n in head.children if not (isinstance(n,Node) and n.tag=='meta' and n.attrs.get('name')=='description')]
    title='QAS · Quechua Aimara Space — '+text_for(locales,lang,'ui.pageTitle').removeprefix('QAS · ')
    root.find(lambda n:n.tag=='title').children=[title]
    head.children.extend(metadata(lang,None,title,text_for(locales,lang,'ui.pageDescription'),config))
    cards=root.find(lambda n:n.attrs.get('class')=='cards')
    cards.children=[render_card(catalog,locales,lang,current,a) for a in catalog['articles'] if a['showCard']]
    notice=root.find(lambda n:n.attrs.get('id')=='language-notice')
    if locales[lang]['meta'].get('needsReview'):
        notice.attrs.pop('hidden',None);notice.children=[text_for(locales,lang,'ui.translationDraft')];notice.attrs['lang']=lang
    noscript=root.find(lambda n:n.tag=='noscript')
    noscript.children=[translated(locales,lang,'ui.noScript','p',{'class':'notice'})]
    footer=root.find(lambda n:n.tag=='footer')
    footer.children.append(language_links(lang,current,label=text_for(locales,lang,'ui.chooseLanguage')))
    body=root.find(lambda n:n.tag=='body')
    routes={code:{a['id']:relative(current,page_path(code,a['id'])) for a in catalog['articles']} for code in LANGUAGES}
    page={'language':lang,'homeLinks':{code:relative(current,page_path(code)) for code in LANGUAGES},'articleLinks':routes}
    config_script=Node('script',children=['window.QAS_PAGE = '+json.dumps(page,ensure_ascii=False).replace('<','\\u003c')+';'])
    first_script=next(i for i,n in enumerate(body.children) if isinstance(n,Node) and n.tag=='script')
    body.children.insert(first_script,config_script)
    return '<!DOCTYPE html>\n'+root.html()

def render_reader(catalog,locales,lang,article,config):
    current=page_path(lang,article['id']);home=relative(current,page_path(lang))
    title=text_for(locales,lang,f'article.{article["id"]}.title')
    description=text_for(locales,lang,f'article.{article["id"]}.summary') if article['showCard'] else text_for(locales,lang,article['paragraphs'][0])
    head=Node('head',children=[Node('meta',{'charset':'utf-8'}),Node('meta',{'name':'viewport','content':'width=device-width, initial-scale=1.0'}),Node('title',children=[title+' · QAS'])])
    head.children.extend(metadata(lang,article['id'],title+' · QAS',description,config))
    for css in ('base','content','design','seo'):
        head.children.append(Node('link',{'rel':'stylesheet','href':relative(current,'assets/'+css+'.css')}))
    header=Node('header',{'class':'reader-header'},[
        Node('a',{'href':home,'class':'brand'},[Node('span',{'class':'brand-name'},['QAS']),Node('span',{'class':'brand-sub'},['Quechua Aimara Space'])]),
        language_links(lang,current,article['id'],text_for(locales,lang,'ui.chooseLanguage'))])
    main=Node('main',{'class':'reader-shell'},[
        translated(locales,lang,'ui.explore','a',{'class':'small-link','href':home+'#explorar'}),
        Node('article',{'class':'reader-article'},[
            Node('div',{'class':'eyebrow'},['QAS · Quechua Aimara Space']),
            Node('h1',{'lang':lang},[title]),
            *([translated(locales,lang,'ui.translationDraft','p',{'class':'notice'})] if locales[lang]['meta'].get('needsReview') else []),
            *article_body(catalog,locales,lang,article)])])
    related=Node('section',{'class':'reader-related'},[translated(locales,lang,'ui.exploreTitle','h2')])
    links=[]
    for other in catalog['articles']:
        if other['showCard'] and other['id']!=article['id']:
            links.append(Node('li',children=[translated(locales,lang,f'article.{other["id"]}.title','a',{'href':relative(current,page_path(lang,other['id']))})]))
    related.children.append(Node('ul',children=links));main.children.append(related)
    footer=Node('footer',{'class':'footer reader-footer'},[
        translated(locales,lang,'ui.contactTitle','a',{'href':home+'#contacto'}),
        translated(locales,lang,'ui.sources','a',{'href':relative(current,page_path(lang,'sources'))}),
        translated(locales,lang,'ui.footer','span')])
    return '<!DOCTYPE html>\n'+Node('html',{'lang':lang},[head,Node('body',children=[header,main,footer])]).html()

def generate_site(root,catalog,locales,config,output=None):
    root=Path(root);output=Path(output or root)
    base=normalize_site_url(config.get('siteUrl'))
    template=(root/'templates/home.html').read_text(encoding='utf-8')
    paths=[]
    for lang in LANGUAGES:
        path=page_path(lang);(output/lang).mkdir(parents=True,exist_ok=True)
        (output/path).write_text(render_home(template,catalog,locales,lang,path,config),encoding='utf-8');paths.append(path)
        for article in catalog['articles']:
            path=page_path(lang,article['id'])
            (output/path).write_text(render_reader(catalog,locales,lang,article,config),encoding='utf-8');paths.append(path)
    (output/'index.html').write_text(render_home(template,catalog,locales,'es','index.html',config),encoding='utf-8')
    (output/'.nojekyll').write_text('',encoding='utf-8')
    robots='User-agent: *\nAllow: /\n'
    if base:
        ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9')
        sitemap=ET.Element('{http://www.sitemaps.org/schemas/sitemap/0.9}urlset')
        for path in paths:
            url=ET.SubElement(sitemap,'{http://www.sitemaps.org/schemas/sitemap/0.9}url')
            ET.SubElement(url,'{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text=base+path
        ET.ElementTree(sitemap).write(output/'sitemap.xml',encoding='utf-8',xml_declaration=True)
        robots+='\nSitemap: '+base+'sitemap.xml\n'
    elif (output/'sitemap.xml').exists():
        # Only remove this generated file so a stale domain cannot be published.
        (output/'sitemap.xml').unlink()
    (output/'robots.txt').write_text(robots,encoding='utf-8')
    manifest={'files':['index.html',*paths,'robots.txt','.nojekyll',*(['sitemap.xml'] if base else [])],
              'siteUrl':base,'canonicalPages':len(paths),'requiresSiteUrl':not bool(base)}
    (output/'site-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifest
