/* 9 个 L1 领域的代码原生 SVG 线条插画，使用经典问题场景。 */
const SVG_NS = 'http://www.w3.org/2000/svg';

function line(x1, y1, x2, y2, extra = {}) {
  return ['line', { x1, y1, x2, y2, 'stroke-width': 1.25, ...extra }];
}

function circle(cx, cy, r, extra = {}) {
  return ['circle', { cx, cy, r, 'stroke-width': 1.5, ...extra }];
}

function ellipse(cx, cy, rx, ry, extra = {}) {
  return ['ellipse', { cx, cy, rx, ry, 'stroke-width': 1.25, ...extra }];
}

function path(d, extra = {}) {
  return ['path', { d, 'stroke-width': 1.5, ...extra }];
}

function rect(x, y, width, height, extra = {}) {
  return ['rect', { x, y, width, height, 'stroke-width': 1.5, ...extra }];
}

function polygon(points, extra = {}) {
  return ['polygon', { points, 'stroke-width': 1.5, ...extra }];
}

function text(x, y, value, extra = {}) {
  return ['text', {
    x,
    y,
    fill: 'currentColor',
    stroke: 'none',
    'font-family': 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
    'font-size': 12,
    'font-weight': 650,
    'text-anchor': 'middle',
    'dominant-baseline': 'central',
    ...extra,
  }, value];
}

function treeNode(cx, cy, radius = 7, value = '') {
  const shapes = [circle(cx, cy, radius, { fill: '#ffffff' })];
  if (value) shapes.push(text(cx, cy + 0.5, value, { 'font-size': radius >= 10 ? 12 : 10 }));
  return shapes;
}

function isometricBrick(x, y, width, height, depth, studs = 2) {
  const top = `${x},${y} ${x + depth},${y - depth / 2} ${x + width + depth},${y - depth / 2} ${x + width},${y}`;
  const side = `${x + width},${y} ${x + width + depth},${y - depth / 2} ${x + width + depth},${y + height - depth / 2} ${x + width},${y + height}`;
  const shapes = [
    rect(x, y, width, height, { fill: '#ffffff', 'stroke-width': 1.8 }),
    polygon(top, { fill: '#ffffff', 'stroke-width': 1.8 }),
    polygon(side, { fill: '#ffffff', 'stroke-width': 1.8 }),
  ];
  for (let index = 0; index < studs; index += 1) {
    const offset = 13 + index * 22;
    shapes.push(ellipse(x + depth / 2 + offset, y - depth / 4, 6, 3.2, { fill: '#ffffff' }));
  }
  return shapes;
}

function queen(cx, cy) {
  return [
    path(`M${cx - 7} ${cy + 6}V${cy + 1}L${cx - 3} ${cy + 4}L${cx - 1} ${cy - 4}L${cx + 2} ${cy + 1}L${cx + 5} ${cy - 5}L${cx + 7} ${cy + 1}V${cy + 6}Z`, { 'stroke-width': 1.7 }),
    line(cx - 4, cy - 8, cx - 4, cy - 10, { 'stroke-width': 1.6 }),
    line(cx, cy - 8, cx, cy - 11, { 'stroke-width': 1.6 }),
    line(cx + 4, cy - 8, cx + 4, cy - 10, { 'stroke-width': 1.6 }),
  ];
}

function eightQueensBoard() {
  const x = 48;
  const y = 8;
  const size = 144;
  const cell = size / 8;
  const shapes = [rect(x, y, size, size, { 'stroke-width': 2.2 })];
  for (let index = 1; index < 8; index += 1) {
    const offset = index * cell;
    shapes.push(line(x + offset, y, x + offset, y + size, { 'stroke-width': 1 }));
    shapes.push(line(x, y + offset, x + size, y + offset, { 'stroke-width': 1 }));
  }
  const columns = [4, 7, 3, 0, 6, 1, 5, 2];
  columns.forEach((column, row) => {
    const cx = x + (column + 0.5) * cell;
    const cy = y + (row + 0.5) * cell;
    shapes.push(...queen(cx, cy));
  });
  return shapes;
}

function dynamicProgrammingSteps() {
  const shapes = [];
  const stepWidth = 29;
  const baseY = 142;
  const startX = 27;
  for (let index = 0; index < 6; index += 1) {
    const x = startX + index * 29;
    const top = 124 - index * 15;
    shapes.push(rect(x, top, stepWidth, baseY - top, { fill: '#ffffff', 'stroke-width': 1.8 }));
  }
  for (let index = 0; index < 5; index += 1) {
    const x = startX + index * 29 + 22;
    const y = 124 - index * 15 - 6;
    const endX = x + 14;
    const endY = y - 13;
    shapes.push(path(`M${x} ${y}C${x + 5} ${y - 7}${endX - 5} ${endY + 3}${endX} ${endY}`, { 'stroke-width': 1.3 }));
    shapes.push(path(`M${endX - 6} ${endY - 1}L${endX} ${endY}L${endX - 1} ${endY + 6}`, { 'stroke-width': 1.3 }));
  }
  return shapes;
}

function trie() {
  const shapes = [];
  const nodes = {
    root: [120, 18], c: [74, 54], d: [166, 54], a: [48, 90], o: [166, 90],
    t: [24, 126], r: [60, 126], n: [96, 126], g: [166, 126],
  };
  const edges = [
    ['root', 'c'], ['root', 'd'], ['c', 'a'], ['d', 'o'],
    ['a', 't'], ['a', 'r'], ['a', 'n'], ['o', 'g'],
  ];
  for (const [from, to] of edges) {
    shapes.push(line(nodes[from][0], nodes[from][1] + 9, nodes[to][0], nodes[to][1] - 9, { 'stroke-width': 1.25 }));
  }
  shapes.push(circle(nodes.root[0], nodes.root[1], 8, { fill: '#ffffff', 'stroke-width': 2 }));
  for (const [name, value] of [['c', 'c'], ['d', 'd'], ['a', 'a'], ['o', 'o'], ['t', 't'], ['r', 'r'], ['n', 'n'], ['g', 'g']]) {
    shapes.push(...treeNode(nodes[name][0], nodes[name][1], 10, value));
  }
  shapes.push(circle(nodes.o[0], nodes.o[1], 13, { 'stroke-width': 1.1 }));
  for (const terminal of ['t', 'r', 'n', 'g']) {
    shapes.push(circle(nodes[terminal][0], nodes[terminal][1], 13, { 'stroke-width': 1.1 }));
  }
  return shapes;
}

function pythagoreanScene() {
  const outer = '60,20 180,20 180,140 60,140';
  const inner = '105,20 180,65 135,140 60,95';
  return [
    polygon(outer, { fill: '#ffffff', 'stroke-width': 2.4 }),
    polygon(inner, { fill: '#ffffff', 'stroke-width': 2 }),
    line(60, 20, 105, 20, { 'stroke-width': 1.3 }),
    line(60, 20, 60, 95, { 'stroke-width': 1.3 }),
    line(105, 20, 60, 95, { 'stroke-width': 1.3 }),
    line(180, 20, 180, 65, { 'stroke-width': 1.3 }),
    line(180, 20, 105, 20, { 'stroke-width': 1.3 }),
    line(180, 65, 105, 20, { 'stroke-width': 1.3 }),
    line(180, 140, 135, 140, { 'stroke-width': 1.3 }),
    line(180, 140, 180, 65, { 'stroke-width': 1.3 }),
    line(135, 140, 180, 65, { 'stroke-width': 1.3 }),
    line(60, 140, 60, 95, { 'stroke-width': 1.3 }),
    line(60, 140, 135, 140, { 'stroke-width': 1.3 }),
    line(60, 95, 135, 140, { 'stroke-width': 1.3 }),
    path('M60 32H72V20', { 'stroke-width': 1.1 }),
    path('M168 20V32H180', { 'stroke-width': 1.1 }),
    path('M180 128H168V140', { 'stroke-width': 1.1 }),
    path('M72 140V128H60', { 'stroke-width': 1.1 }),
  ];
}

function balancedTree() {
  const positions = {
    4: [120, 28], 2: [76, 72], 6: [164, 72], 1: [48, 116], 3: [104, 116],
    5: [140, 116], 7: [190, 116],
  };
  const edges = [[4, 2], [4, 6], [2, 1], [2, 3], [6, 5], [6, 7]];
  const shapes = edges.map(([from, to]) => line(positions[from][0], positions[from][1] + 11, positions[to][0], positions[to][1] - 11, { 'stroke-width': 1.45 }));
  for (const [value, [x, y]] of Object.entries(positions)) shapes.push(...treeNode(x, y, 12, value));
  for (const x of [48, 104, 140, 190]) shapes.push(rect(x - 3, 137, 6, 6, { fill: 'currentColor', 'stroke-width': 0 }));
  return shapes;
}

function shortestPathGraph() {
  const edges = [
    [34, 80, 80, 38], [34, 80, 80, 122], [80, 38, 124, 80],
    [80, 122, 124, 80], [80, 38, 170, 44], [80, 122, 170, 116],
    [124, 80, 170, 44], [124, 80, 170, 116], [170, 44, 208, 80], [170, 116, 208, 80],
  ];
  const shapes = edges.map(([x1, y1, x2, y2]) => line(x1, y1, x2, y2, {
    'stroke-width': 1.1,
    'stroke-dasharray': '4 4',
  }));
  shapes.push(['polyline', {
    points: '34,80 80,122 124,80 170,44 208,80',
    'stroke-width': 3.4,
  }]);
  for (const [cx, cy] of [[34, 80], [80, 38], [80, 122], [124, 80], [170, 44], [170, 116], [208, 80]]) {
    shapes.push(circle(cx, cy, 7, { fill: '#ffffff' }));
  }
  shapes.push(circle(34, 80, 10, { 'stroke-width': 1.2 }));
  shapes.push(circle(208, 80, 10, { 'stroke-width': 1.2 }));
  return shapes;
}

function convexHull() {
  const hull = [
    [34, 118], [50, 50], [82, 24], [132, 32], [186, 66], [208, 116], [150, 138], [86, 132],
  ];
  const shapes = [polygon(hull.map(([x, y]) => `${x},${y}`).join(' '), { 'stroke-width': 2.4 })];
  for (const [x, y] of [[82, 68], [118, 90], [68, 100], [142, 104], [108, 54], [176, 102]]) {
    shapes.push(circle(x, y, 3, { fill: 'currentColor', 'stroke-width': 0 }));
  }
  for (const [x, y] of hull) shapes.push(circle(x, y, 4.5, { fill: '#ffffff', 'stroke-width': 1.6 }));
  shapes.push(path('M50 50A34 34 0 0 1 69 34', { 'stroke-width': 1.1 }));
  return shapes;
}

function twoPointers() {
  const values = [1, 3, 4, 7, 9, 12, 15, 19, 23];
  const cellWidth = 22;
  const startX = 18;
  const y = 64;
  const shapes = [];
  values.forEach((value, index) => {
    const x = startX + index * cellWidth;
    shapes.push(rect(x, y, cellWidth, 34, { fill: '#ffffff', 'stroke-width': 1.35 }));
    shapes.push(text(x + cellWidth / 2, y + 17, value, { 'font-size': 10 }));
  });
  const centerPointer = startX + 4 * cellWidth + cellWidth / 2;
  const leftPointer = startX + cellWidth / 2;
  const rightPointer = startX + 8 * cellWidth + cellWidth / 2;
  shapes.push(path(`M${leftPointer} ${y}V${y - 24}H${centerPointer}V${y - 6}`, { 'stroke-width': 2.4 }));
  shapes.push(path(`M${centerPointer - 6} ${y - 6}L${centerPointer} ${y}L${centerPointer + 6} ${y - 6}`, { 'stroke-width': 2.4 }));
  shapes.push(path(`M${rightPointer} ${y + 34}V${y + 58}H${centerPointer}V${y + 40}`, { 'stroke-width': 2.4 }));
  shapes.push(path(`M${centerPointer - 6} ${y + 40}L${centerPointer} ${y + 34}L${centerPointer + 6} ${y + 40}`, { 'stroke-width': 2.4 }));
  return shapes;
}

const DRAWINGS = {
  'basic': [
    ...isometricBrick(42, 88, 58, 40, 20, 2),
    ...isometricBrick(112, 98, 62, 30, 18, 2),
    ...isometricBrick(82, 44, 54, 38, 18, 2),
  ],
  'search': eightQueensBoard(),
  'dp': dynamicProgrammingSteps(),
  'string': trie(),
  'math': pythagoreanScene(),
  'ds': balancedTree(),
  'graph': shortestPathGraph(),
  'geometry': convexHull(),
  'misc': twoPointers(),
};

const FALLBACK = [
  ...treeNode(120, 46, 10),
  ...treeNode(72, 112, 9),
  ...treeNode(168, 112, 9),
  line(113, 56, 77, 103, { 'stroke-width': 1.5 }),
  line(127, 56, 163, 103, { 'stroke-width': 1.5 }),
];

export function knowledgeIllustration(id, { label = '', className = '' } = {}) {
  const svg = document.createElementNS(SVG_NS, 'svg');
  svg.setAttribute('viewBox', '0 0 240 160');
  svg.setAttribute('fill', 'none');
  svg.setAttribute('stroke', 'currentColor');
  svg.setAttribute('stroke-width', '1.5');
  svg.setAttribute('stroke-linecap', 'round');
  svg.setAttribute('stroke-linejoin', 'round');
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', label || '知识示意图');
  svg.setAttribute('class', ['knowledge-illustration', className].filter(Boolean).join(' '));
  for (const [tag, attributes, value] of DRAWINGS[id] || FALLBACK) {
    const node = document.createElementNS(SVG_NS, tag);
    for (const [key, attribute] of Object.entries(attributes)) {
      if (attribute !== null && attribute !== undefined) node.setAttribute(key, String(attribute));
    }
    if (value !== undefined) node.textContent = value;
    svg.append(node);
  }
  return svg;
}
