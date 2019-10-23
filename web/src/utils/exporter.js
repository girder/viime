// eslint-disable-next-line import/no-webpack-loader-syntax
import font from '!url-loader?limit=undefined!@openfonts/barlow-condensed_all/files/barlow-condensed-all-400.woff2';
import { unparse } from 'papaparse';


export function svg2png(svgElement, options = {}) {
  const findStyles = options.styles !== false;
  const returnSvg = options.return === 'svg';

  // based on http://bl.ocks.org/biovisualize/8187844
  const copy = svgElement.cloneNode(true);
  // proper bg
  copy.style.backgroundColor = 'white';
  // inject font
  copy.style.fontFamily = 'Barlow Condensed, sans-serif';
  copy.insertAdjacentHTML('afterbegin', `<style>
    /* barlow-condensed-400normal - all */
    @font-face {
      font-family: 'Barlow Condensed';
      font-style: normal;
      font-display: swap;
      font-weight: 400;
      src:
        local('Barlow Condensed Regular'),
        local('BarlowCondensed-Regular'),
        url('${font}') format('woff2')
    }
  </style>`);

  // find related style sheets
  const scopedAttr = Array.from(copy.getAttributeNames()).find(d => d.startsWith('data-v-'));
  if (findStyles && scopedAttr) {
    const key = `[${scopedAttr}]`;
    const rules = [];
    Array.from(document.styleSheets).forEach((sheet) => {
      if (sheet instanceof CSSStyleSheet) {
        try {
          Array.from(sheet.cssRules).forEach((rule) => {
            if (rule.cssText.includes(key)) {
              rules.push(rule.cssText);
            }
          });
        } catch {
          // ignore
        }
      }
    });
    copy.insertAdjacentHTML('afterbegin', `<style>${rules.join('\n')}</style>`);
  }

  const svgString = new XMLSerializer().serializeToString(copy);
  const svg = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
  const svgUrl = URL.createObjectURL(svg);

  if (returnSvg) {
    return Promise.resolve(svgUrl);
  }

  const canvas = document.createElement('canvas');

  const bb = svgElement.getBoundingClientRect();
  canvas.width = bb.width;
  canvas.height = bb.height;
  const ctx = canvas.getContext('2d');
  const img = new Image(canvas.width, canvas.height);

  return new Promise((resolve) => {
    img.onload = () => {
      ctx.drawImage(img, 0, 0);
      URL.revokeObjectURL(svgUrl);
      const png = canvas.toDataURL('image/png');
      resolve(png);
    };
    img.src = svgUrl;
  });
}

export function download(url, title) {
  const a = document.createElement('a');
  a.href = url;
  a.style.position = 'absolute';
  a.style.left = '-10000px';
  a.style.top = '-10000px';
  a.download = title;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

export function downloadCSV(content, title) {
  let data = content;
  if (typeof content !== 'string') {
    data = unparse(content);
  }
  const csv = new Blob([data], { type: 'text/csv;charset=utf-8' });
  const csvUrl = URL.createObjectURL(csv);
  download(csvUrl, `${title}.csv`);
  URL.revokeObjectURL(csvUrl);
}

export async function downloadSVG(svgElement, title = 'Image') {
  const url = await svg2png(svgElement);
  download(url, `${title}.png`);
}
