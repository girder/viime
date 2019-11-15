// eslint-disable-next-line import/no-webpack-loader-syntax
import font from '!url-loader?limit=undefined!@openfonts/barlow-condensed_all/files/barlow-condensed-all-400.woff2';
// eslint-disable-next-line import/no-webpack-loader-syntax
import iconFont from '!url-loader?limit=undefined!@mdi/font/fonts/materialdesignicons-webfont.woff2';
import { unparse } from 'papaparse';


function isC3(node: SVGSVGElement) {
  return node.querySelector('.c3-chart') != null;
}

function fixC3SVG(node: SVGSVGElement) {
  // See
  // https://stackoverflow.com/questions/37701361/exporting-c3-js-line-charts-to-png-images-does-not-work.
  node.insertAdjacentHTML('afterbegin', `<style>
    /* c3-chart considerations */
    path.domain {
      fill: none;
      stroke: black;
    }

    .tick line {
      stroke: black;
    }
  </style>`);

  // For some reason, C3 uses the "color" style property instead of "fill".
  Array.from(node.querySelectorAll('circle')).forEach((circle) => {
    circle.style.fill = circle.style.color;
    delete circle.style.color;
  });
  return node;
}

function findScopedAttr(elem: Element) {
  let names = [];
  if (typeof elem.getAttributeNames === 'function') {
    names = Array.from(elem.getAttributeNames());
  } else {
    // like edge
    names = Array.from(elem.attributes).map(attr => attr.name);
  }
  return names.find(d => d.startsWith('data-v-'));
}

export interface IExporterOptions {
  styles: boolean;
  font: boolean;
  icons: boolean;
}

export function svg2url(svgElement: SVGSVGElement, options: Partial<IExporterOptions> = {}) {
  const findStyles = options.styles !== false;
  const includeFont = options.font !== false;
  const includeIconFont = options.icons;

  // based on http://bl.ocks.org/biovisualize/8187844
  let copy = svgElement.cloneNode(true) as SVGSVGElement;
  // proper bg
  copy.style.backgroundColor = 'white';
  // inject font
  if (includeFont) {
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
          url('${font}') format('woff2');
      }
    </style>`);
  }
  if (includeIconFont) {
    copy.insertAdjacentHTML('afterbegin', `<style>
      /* MaterialDesignIcons.com */
      @font-face {
        font-family: "Material Design Icons";
        src:
          url('${iconFont}') format('woff2');
        font-weight: normal;
        font-style: normal;
    }
    </style>`);
  }

  // find related style sheets
  const scopedAttr = findScopedAttr(copy);
  if (findStyles && scopedAttr) {
    const key = `[${scopedAttr}]`;
    const rules: string[] = [];
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

  // Need some special treatment for C3 charts.
  if (isC3(copy)) {
    copy = fixC3SVG(copy);
  }

  const svgString = new XMLSerializer().serializeToString(copy);
  const svg = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
  return URL.createObjectURL(svg);
}

export function renderImage(imgUrl: string, bb: DOMRect | ClientRect) {
  const canvas = document.createElement('canvas');

  canvas.width = bb.width;
  canvas.height = bb.height;
  const ctx = canvas.getContext('2d')!;
  const img = new Image(canvas.width, canvas.height);

  return new Promise<string>((resolve) => {
    img.onload = () => {
      ctx.drawImage(img, 0, 0);
      const png = canvas.toDataURL('image/png');
      resolve(png);
    };
    img.src = imgUrl;
  });
}

export function svg2png(svgElement: SVGSVGElement, options: Partial<IExporterOptions> = {}) {
  const svgUrl = svg2url(svgElement, options);

  return renderImage(svgUrl, svgElement.getBoundingClientRect()).then((img) => {
    URL.revokeObjectURL(svgUrl);
    return img;
  });
}

export function download(url: string, title: string) {
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

export function downloadCSV(content: string, title: string) {
  let data = content;
  if (typeof content !== 'string') {
    data = unparse(content);
  }
  const csv = new Blob([data], { type: 'text/csv;charset=utf-8' });
  const csvUrl = URL.createObjectURL(csv);
  download(csvUrl, `${title}.csv`);
  URL.revokeObjectURL(csvUrl);
}

export async function downloadSVG(svgElement: SVGSVGElement, title = 'Image') {
  const url = await svg2png(svgElement);
  download(url, `${title}.png`);
}
