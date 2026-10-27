'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const core = require('./exporter');

test('discovers page/view pairs without treating code examples as embeds', () => {
  const source = '![[Books.base]]\n![[Books.base#OnTopicPage]]\n![[Books.base]]\n`![[Code.base]]`\n```\n![[Fence.base]]\n```\n    ![[Indented.base]]\n';
  assert.deepEqual(core.findEmbeds(source).map(item => item.key), ['Books.base', 'Books.base#OnTopicPage']);
});

test('preserves the original query; Obsidian remains the only evaluator', () => {
  const base = {filters: {and: ['file.hasTag("book")']}, formulas: {score: 'price*2'},
    views: [{type: 'table', name: 'All', order: ['file.name']},
      {type: 'table', name: 'OnTopicPage', filters: {and: ['file.links.contains(this)']}, sort: [{property: 'formula.score', direction: 'DESC'}], limit: 50}]};
  const before = JSON.stringify(base);
  const result = core.selectView(base, 'OnTopicPage');
  assert.equal(result.filters, base.filters);
  assert.equal(result.formulas, base.formulas);
  assert.deepEqual(result.views[0], {...base.views[1], type: core.VIEW_TYPE});
  assert.equal(JSON.stringify(base), before);
  assert.equal(core.selectView(base, null).views[0].name, 'All');
  assert.throws(() => core.selectView(base, 'Missing'), /not found/);
  assert.throws(() => core.selectView({views: [{type: 'cards'}]}, null), /Unsupported/);
});

function entry(name, score) {
  return {file: {path: 'books/' + name + '.md', basename: name},
    getValue: id => ({toString: () => id === 'file.name' ? name : score})};
}

test('exports all rows in native order, not just the visible viewport', () => {
  const rows = Array.from({length: 1500}, (_, i) => entry('Book (' + (1499-i) + ') #1', String(i)));
  const view = {config: {getOrder: () => ['file.name', 'formula.score'], getDisplayName: id => id},
    data: {groupedData: [{hasKey: () => false, entries: rows}]}};
  const output = core.tableSnapshot(view, 'topics/Topic.md');
  assert.equal(output.split('\n').filter(line => line.startsWith('| [')).length, 1500);
  assert.ok(output.indexOf('Book (1499)') < output.indexOf('Book (0)'));
  assert.ok(output.includes('../books/Book%20%281499%29%20%231.md'));
  assert.ok(output.includes('| 1499 |'));
});

test('keeps native groups and represents an empty result as a table', () => {
  const config = {getOrder: () => ['file.name'], getDisplayName: () => 'Name'};
  const output = core.tableSnapshot({config, data: {groupedData: [
    {hasKey: () => true, key: {toString: () => 'Group B'}, entries: [entry('B', 2)]},
    {hasKey: () => true, key: {toString: () => 'Group A'}, entries: [entry('A', 1)]},
  ]}}, 'books/index.md');
  assert.ok(output.indexOf('Group B') < output.indexOf('Group A'));
  assert.equal(core.tableSnapshot({config, data: {groupedData: []}}, 'books/index.md'), '| Name |\n| --- |\n\n');
});

test('input fingerprint tracks new, modified, renamed and deleted notes, ignoring plugin state', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'wiki-exporter-'));
  try {
    await fs.writeFile(path.join(root, 'note.md'), 'original');
    const first = await core.inputDigest(root);
    await fs.mkdir(path.join(root, '.obsidian'));
    await fs.writeFile(path.join(root, '.obsidian/data.md'), 'plugin state');
    assert.equal(await core.inputDigest(root), first);
    await fs.writeFile(path.join(root, 'note.md'), 'changed');
    const modified = await core.inputDigest(root);
    assert.notEqual(modified, first);
    await fs.rename(path.join(root, 'note.md'), path.join(root, 'renamed.md'));
    assert.notEqual(await core.inputDigest(root), modified);
    await fs.writeFile(path.join(root, 'new.md'), 'new');
    const added = await core.inputDigest(root);
    await fs.unlink(path.join(root, 'new.md'));
    assert.notEqual(await core.inputDigest(root), added);
  } finally { await fs.rm(root, {recursive: true, force: true}); }
});

test('native summary values are exported without recomputing them', () => {
  const controller = {};
  const rows = [entry('One', 1), entry('Two', 2)];
  let called = false;
  const view = {
    queryController: controller,
    config: {getOrder: () => ['formula.score'], getDisplayName: () => 'Score', get: () => ({'formula.score': 'Sum'})},
    data: {groupedData: [{hasKey: () => false, entries: rows}],
      getSummaryValue: (query, entries, prop, summary) => {
        assert.equal(query, controller);
        assert.equal(entries, rows);
        assert.equal(prop, 'formula.score');
        assert.equal(summary, 'Sum');
        called = true;
        return {toString: () => 'Native summary'};
      }},
  };
  assert.ok(core.tableSnapshot(view, 'index.md').includes('| Native summary |'));
  assert.ok(called);
});
