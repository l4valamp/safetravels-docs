'use strict';
const crypto = require('crypto');
const fs = require('fs/promises');
const path = require('path');

const VIEW_TYPE = 'reading-wiki-snapshot';

function findEmbeds(markdown) {
  const results = [];
  let fence = null;
  for (const line of markdown.split(/\r?\n/)) {
    const marker = line.match(/^ {0,3}(`{3,}|~{3,})/);
    if (marker) {
      const token = marker[1];
      if (!fence) fence = token;
      else if (token[0] === fence[0] && token.length >= fence.length) fence = null;
      continue;
    }
    if (fence || /^(    |\t)/.test(line)) continue;
    const text = line.replace(/(`+).*?\1/g, '');
    for (const match of text.matchAll(/!\[\[([^\]#]+?\.base)(?:#([^\]]+))?\]\]/gi)) {
      const base = match[1].trim().replace(/\\/g, '/');
      const view = match[2]?.trim() || null;
      const key = base + (view ? '#' + view : '');
      if (!results.some(item => item.key === key)) results.push({ base, view, key });
    }
  }
  return results;
}

function selectView(base, requested) {
  if (!base || !Array.isArray(base.views) || !base.views.length) {
    throw new Error('Base has no views.');
  }
  const view = requested ? base.views.find(view => view.name === requested) : base.views[0];
  if (!view) throw new Error(`Base view not found: ${requested}`);
  if (view.type !== 'table') throw new Error(`Unsupported view type ${view.type}; expected a table.`);
  // This is a temporary, in-memory rendering configuration. Obsidian still
  // evaluates the unchanged global/view filters, formulas, sorting and limits.
  return { ...base, views: [{ ...view, type: VIEW_TYPE }] };
}

function cell(value) {
  return String(value ?? '').replace(/\r?\n/g, '<br>').replace(/\|/g, '\\|');
}
function label(value) {
  return cell(value).replace(/([\[\]<>])/g, '\\$1');
}
function fileLink(file, page, text) {
  const relative = path.posix.relative(path.posix.dirname(page), file.path);
  const href = relative.split('/').map(segment => encodeURIComponent(segment).replace(/[()]/g, c => '%' + c.charCodeAt(0).toString(16))).join('/');
  return `[${label(text || file.basename)}](${href})`;
}

function tableSnapshot(view, page) {
  const properties = view.config.getOrder();
  const columns = properties.length ? properties : view.data.properties;
  if (!columns.length) throw new Error('Obsidian returned no visible properties.');
  const lines = [];
  const header = '| ' + columns.map(id => cell(view.config.getDisplayName(id))).join(' | ') + ' |';
  const separator = '| ' + columns.map(() => '---').join(' | ') + ' |';
  const groups = view.data.groupedData;
  for (const group of groups) {
    if (group.hasKey()) lines.push('### ' + cell(group.key.toString()), '');
    lines.push(header, separator);
    for (const entry of group.entries) {
      const values = columns.map(id => {
        const value = entry.getValue(id);
        if (id === 'file.name' || id === 'file.basename') return fileLink(entry.file, page, value?.toString());
        return cell(value?.toString() ?? '');
      });
      lines.push('| ' + values.join(' | ') + ' |');
    }
    const summaries = view.config.get?.('summaries') || {};
    if (columns.some(id => summaries[id])) {
      lines.push('| ' + columns.map(id => summaries[id]
        ? cell(view.data.getSummaryValue(view.queryController, group.entries, id, summaries[id]).toString())
        : '').join(' | ') + ' |');
    }
    lines.push('');
  }
  // An empty query is a valid result, not a missing export.
  if (!groups.length) lines.push(header, separator, '');
  return lines.join('\n') + '\n';
}

async function inputDigest(vaultRoot, contentOnly = false) {
  const entries = [];
  async function walk(folder) {
    for (const item of await fs.readdir(folder, { withFileTypes: true })) {
      if (item.name.startsWith('.')) continue;
      const absolute = path.join(folder, item.name);
      if (item.isDirectory()) await walk(absolute);
      else if (item.isFile() && /\.(md|base)$/i.test(item.name)) {
        const relative = path.relative(vaultRoot, absolute).split(path.sep).join('/');
        let bytes = await fs.readFile(absolute);
        if (contentOnly) bytes = Buffer.from(bytes.toString('utf8').replace(/\r\n/g, '\n'));
        const modified = contentOnly ? '' : (await fs.stat(absolute, { bigint: true })).mtimeNs.toString();
        entries.push([relative, crypto.createHash('sha256').update(bytes).digest('hex'), modified]);
      }
    }
  }
  await walk(vaultRoot);
  entries.sort((a, b) => Buffer.compare(Buffer.from(a[0]), Buffer.from(b[0])));
  const hash = crypto.createHash('sha256');
  for (const [name, digest, modified] of entries) hash.update(name + '\0' + digest + '\0' + modified + '\n');
  return hash.digest('hex');
}

async function atomicWrite(filename, text) {
  await fs.mkdir(path.dirname(filename), { recursive: true });
  const temp = filename + '.' + crypto.randomUUID() + '.tmp';
  try { await fs.writeFile(temp, text, 'utf8'); await fs.rename(temp, filename); }
  finally { await fs.rm(temp, { force: true }); }
}

function snapshotName(page, embed) {
  return 'generated/' + crypto.createHash('sha256').update(page + '\0' + embed).digest('hex') + '.md';
}

module.exports = { VIEW_TYPE, findEmbeds, selectView, tableSnapshot, inputDigest, atomicWrite, snapshotName };
