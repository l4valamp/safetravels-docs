'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');

function plugin() {
  const sandbox = {
    module: { exports: {} },
    require: name => name === 'obsidian' ? { Plugin: class {}, BasesView: class {} } : require(name),
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, 'main.js'), 'utf8'), sandbox);
  return new sandbox.module.exports();
}

test('automatic exports quietly retry concurrent edits, including without another save event', async () => {
  const instance = plugin();
  let retries = 0;
  instance.schedule = () => retries++;
  instance.report = () => assert.fail('Concurrent edits should not show an error');
  instance.exportAll = async () => { throw Object.assign(new Error('changed'), { code: 'NOTES_CHANGED' }); };
  await instance.exportAutomatically();
  assert.equal(retries, 1);
  assert.equal(instance.autoExportPending, false);
});

test('coalesces automatic exports while a run is pending', async () => {
  const instance = plugin();
  let finish;
  let runs = 0;
  let retries = 0;
  instance.exportAll = () => { runs++; return new Promise(resolve => { finish = resolve; }); };
  instance.schedule = () => retries++;
  const running = instance.exportAutomatically();
  await instance.exportAutomatically();
  await instance.exportAutomatically();
  assert.equal(runs, 1);
  finish();
  await running;
  assert.equal(retries, 1);
});

test('reports real failures and does not retry after unloading', async () => {
  const instance = plugin();
  const error = new Error('Missing Base');
  const reported = [];
  instance.report = error => reported.push(error);
  instance.schedule = () => assert.fail('Unexpected retry');
  instance.exportAll = async () => { throw error; };
  await instance.exportAutomatically();
  assert.deepEqual(reported, [error]);
  instance.stopped = true;
  instance.exportAll = async () => { throw Object.assign(new Error('changed'), { code: 'NOTES_CHANGED' }); };
  await instance.exportAutomatically();
});
