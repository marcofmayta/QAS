"""Package only public QAS files. Does not deploy or contact any service."""
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    manifest=json.loads((ROOT/'site-manifest.json').read_text(encoding='utf-8'))
    files=[ROOT/path for path in manifest['files']]
    files.extend(path for path in (ROOT/'assets').iterdir() if path.suffix in ('.js','.css'))
    files.extend((ROOT/'contenido').glob('lectura-*.md'))
    for path in files:
        if not path.resolve().is_relative_to(ROOT) or not path.is_file():
            raise ValueError(f'Archivo público inválido: {path}')
    output=ROOT/'publicacion';output.mkdir(exist_ok=True)
    archive=output/'qas-piloto.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(set(files)):bundle.write(path,path.relative_to(ROOT).as_posix())
    print(f'ZIP: {archive} ({len(set(files))} archivos públicos)')
    if manifest['requiresSiteUrl']:
        print('Sin URL pública configurada: este ZIP todavía no incluye sitemap ni enlaces canónicos absolutos.')

if __name__=='__main__':main()
