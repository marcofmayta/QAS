'use strict';

window.QASShare = {
  create(title, content, url, messages, draft) {
    const section = document.createElement('section');
    section.className = 'article-share';
    const heading = document.createElement('h3');
    heading.textContent = messages['ui.shareLinkedIn'];
    const help = document.createElement('p');
    help.textContent = messages['ui.shareHelp'];
    const text = document.createElement('textarea');
    text.readOnly = true;
    text.rows = 6;
    text.setAttribute('aria-label', messages['ui.shareText']);
    text.value = [title, 'QAS · Quechua Aimara Space', draft, content, url].filter(Boolean).join('\n\n');
    const copy = document.createElement('button');
    copy.type = 'button';
    copy.className = 'button';
    copy.textContent = messages['ui.copyPost'];
    const link = document.createElement('a');
    link.className = 'button';
    link.href = 'https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(url);
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = messages['ui.shareLinkedIn'];
    const status = document.createElement('p');
    status.setAttribute('role', 'status');
    const count = document.createElement('p');
    count.textContent = `${Array.from(text.value).length} / 3.000`;
    const download = document.createElement('button');
    download.type = 'button';
    download.className = 'button';
    download.textContent = messages['ui.shareImage'];
    download.addEventListener('click', () => {
      const canvas = document.createElement('canvas');
      canvas.width = 1200;
      const ctx = canvas.getContext('2d');
      const lines = [];
      const wrap = (value, size, color) => {
        ctx.font = `${size}px sans-serif`;
        for (const paragraph of value.split('\n')) {
          let line = '';
          for (const char of Array.from(paragraph)) {
            if (ctx.measureText(line + char).width > 1020) {
              lines.push({text:line,size,color}); line = '';
            }
            line += char;
          }
          lines.push({text:line,size,color});
        }
      };
      wrap(title, 52, '#d4ed9a');
      wrap('\n' + [draft, content].filter(Boolean).join('\n\n'), 28, '#e2eaf0');
      wrap('\n' + url, 23, '#d4ed9a');
      canvas.height = Math.ceil(260 + lines.reduce((sum,line) => sum + line.size * 1.5, 0));
      ctx.fillStyle = '#091721'; ctx.fillRect(0,0,1200,canvas.height);
      ctx.fillStyle = '#d4ed9a'; ctx.fillRect(0,0,1200,10);
      ctx.font = 'bold 32px sans-serif'; ctx.fillText('QAS · Quechua Aimara Space',90,100);
      let y=190;
      for (const line of lines) {
        ctx.font = `${line.size}px sans-serif`; ctx.fillStyle = line.color;
        ctx.fillText(line.text,90,y); y += line.size * 1.5;
      }
      canvas.toBlob(blob => {
        if (!blob) return;
        const imageURL = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href=imageURL; anchor.download='QAS-'+url.split('/').pop().replace('.html','')+'.png';
        anchor.click(); setTimeout(() => URL.revokeObjectURL(imageURL),1000);
      }, 'image/png');
    });
    copy.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(text.value);
        status.textContent = messages['ui.postCopied'];
      } catch {
        text.focus();
        text.select();
        status.textContent = messages['ui.copyManually'];
      }
    });
    const details = document.createElement('details');
    const summary = document.createElement('summary');
    summary.textContent = messages['ui.shareText'];
    details.append(summary, text, count, copy);
    section.append(heading, help, download, link, details, status);
    return section;
  }
};

const reader = document.querySelector('.reader-article');
const shareData = document.getElementById('share-data');
if (reader && shareData) {
  const data = JSON.parse(shareData.textContent);
  reader.append(window.QASShare.create(data.title, data.content, data.url, data.messages, data.draft));
}
