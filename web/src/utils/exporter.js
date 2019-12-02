export function svg2url(svgElement, options = {}) {
  return import('./exporter_lazy').then(mod => mod.svg2url(svgElement, options));
}

export function renderImage(imgUrl, bb) {
  const canvas = document.createElement('canvas');

  canvas.width = bb.width;
  canvas.height = bb.height;
  const ctx = canvas.getContext('2d');
  const img = new Image(canvas.width, canvas.height);

  return new Promise((resolve) => {
    img.onload = () => {
      ctx.drawImage(img, 0, 0);
      const png = canvas.toDataURL('image/png');
      resolve(png);
    };
    img.src = imgUrl;
  });
}

function jsoncsv2url(content) {
  return import('./exporter_lazy').then(mod => mod.jsoncsv2url(content));
}

export async function svg2png(svgElement, options) {
  const svgUrl = await svg2url(svgElement, options);
  const img = await renderImage(svgUrl, svgElement.getBoundingClientRect());
  URL.revokeObjectURL(svgUrl);
  return img;
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

export async function downloadCSV(content, title) {
  const csvUrl = await jsoncsv2url(content);
  download(csvUrl, `${title}.csv`);
  URL.revokeObjectURL(csvUrl);
}

export async function downloadSVG(svgElement, title = 'Image') {
  const url = await svg2png(svgElement);
  download(url, `${title}.png`);
}
