'use strict';
const { Plugin, BasesView, MarkdownRenderer, Component, Notice, parseYaml, stringifyYaml } = require('obsidian');
const fs = require('fs/promises');
const path = require('path');
const crypto = require('crypto');
// Browser timers are throttled when Obsidian is minimized. The desktop
// exporter must keep processing saves/builds while the window is inactive.
const { setTimeout, clearTimeout, setInterval, clearInterval } = require('timers');
const core = require('./exporter');

class SnapshotView extends BasesView {
  constructor(controller, capture) {
    super(controller);
    this.type = core.VIEW_TYPE;
    this.queryController = controller;
    this.capture = capture;
  }
  onDataUpdated() {
    if (this.capture) this.capture.updated(this);
  }
}

module.exports = class ReadingWikiExporter extends Plugin {
  async onload() {
    if (!this.app.vault.adapter.getBasePath) throw new Error('Reading Wiki exporter requires a local desktop vault.');
    this.vaultRoot = this.app.vault.adapter.getBasePath();
    this.projectRoot = path.dirname(this.vaultRoot);
    this.bridge = path.join(this.vaultRoot, this.app.vault.configDir, 'plugins', this.manifest.id, 'bridge');
    await fs.mkdir(path.join(this.bridge, 'requests'), { recursive: true });
    this.queue = Promise.resolve();
    this.handling = new Set();
    this.activeCapture = null;
    this.stopped = false;
    if (!this.registerBasesView(core.VIEW_TYPE, {
      name: 'Reading Wiki snapshot', icon: 'download',
      factory: (controller) => new SnapshotView(controller, this.activeCapture),
    })) throw new Error('Enable Obsidian Bases before enabling Reading Wiki Exporter.');
    this.addCommand({ id: 'export-all', name: 'Export all database views now', callback: () => {
      this.exportAll().then(result => new Notice(`Exported ${result.views} database views.`)).catch(error => this.report(error));
    } });
    const changed = (file) => {
      if (file && /\.(md|base)$/i.test(file.path)) this.schedule();
    };
    for (const event of ['create', 'modify', 'delete', 'rename']) {
      this.registerEvent(this.app.vault.on(event, changed));
    }
    this.registerEvent(this.app.metadataCache.on('resolved', () => this.schedule()));
    const pollTimer = setInterval(() => this.poll().catch(error => this.report(error)), 400);
    this.register(() => clearInterval(pollTimer));
    this.app.workspace.onLayoutReady(() => this.schedule());
  }

  onunload() {
    this.stopped = true;
    clearTimeout(this.debounce);
    this.activeCapture?.reject(new Error('Reading Wiki exporter was unloaded.'));
  }

  report(error) {
    console.error('[Reading Wiki exporter]', error);
    new Notice(`Reading Wiki export failed: ${error.message}`, 10000);
  }

  schedule() {
    clearTimeout(this.debounce);
    this.debounce = setTimeout(() => {
      if (!this.stopped) this.exportAutomatically();
    }, 1500);
  }

  async exportAutomatically() {
    // Coalesce saves while an export is queued or running. Retry only after
    // the current run finishes and editing has had another quiet interval.
    if (this.autoExportPending) {
      this.autoExportAgain = true;
      return;
    }
    this.autoExportPending = true;
    try {
      await this.exportAll();
    } catch (error) {
      if (error.code === 'NOTES_CHANGED') this.autoExportAgain = true;
      else this.report(error);
    } finally {
      this.autoExportPending = false;
      if (this.autoExportAgain) {
        this.autoExportAgain = false;
        if (!this.stopped) this.schedule();
      }
    }
  }

  exportAll(pages = null) {
    const result = this.queue.catch(() => {}).then(() => this.runExport(pages));
    this.queue = result;
    return result;
  }

  async poll() {
    const folder = path.join(this.bridge, 'requests');
    for (const name of await fs.readdir(folder)) {
      if (!/^[a-f0-9-]+\.json$/.test(name) || this.handling.has(name)) continue;
      this.handling.add(name);
      // Each request has its own response; concurrent builds cannot consume
      // one another's acknowledgement.
      (async () => {
        const requestFile = path.join(folder, name);
        let response;
        try {
          const request = JSON.parse(await fs.readFile(requestFile, 'utf8'));
          if (request.id + '.json' !== name) throw new Error('Invalid export request ID.');
          if (Date.now() - request.createdAt > 120000) throw new Error('Export request expired; rerun the build.');
          const result = await this.exportAll(request.pages);
          response = { id: request.id, ok: true, ...result };
        } catch (error) { response = { ok: false, error: error.message }; }
        await core.atomicWrite(path.join(this.bridge, name), JSON.stringify(response));
        await fs.rm(requestFile, { force: true });
      })().catch(error => this.report(error)).finally(() => this.handling.delete(name));
    }
  }

  async settings() {
    // MkDocs has Python-specific YAML tags that Obsidian cannot parse.
    // The installer extracts just the exporter settings as plain JSON.
    const config = JSON.parse(await fs.readFile(path.join(this.projectRoot, 'obsidian-export.json'), 'utf8'));
    const docs = path.resolve(this.projectRoot, config.docs_dir || 'docs');
    if (docs !== path.resolve(this.vaultRoot)) throw new Error('This vault must be the docs_dir of the adjacent mkdocs.yml.');
    const registration = (config.plugins || []).find(item => item && typeof item === 'object' && 'databaseview' in item);
    const relative = registration?.databaseview?.snapshot_manifest || 'database-snapshots/manifest.yml';
    const manifestPath = path.resolve(this.projectRoot, relative);
    if (!manifestPath.startsWith(this.projectRoot + path.sep) || manifestPath.startsWith(this.vaultRoot + path.sep)) {
      throw new Error('snapshot_manifest must be inside the project and outside the vault.');
    }
    return { manifestPath };
  }

  async runExport(requestedPages) {
    if (this.stopped) throw new Error('Exporter is unloaded.');
    const { manifestPath } = await this.settings();
    const directory = path.dirname(manifestPath);
    const before = await core.inputDigest(this.vaultRoot);
    const available = this.app.vault.getMarkdownFiles();
    const files = requestedPages ? requestedPages.map(page => {
      const file = this.app.vault.getFileByPath(page);
      if (!file || file.extension !== 'md') throw new Error(`Source page not found: ${page}`);
      return file;
    }) : available.filter(file => !file.path.split('/').some(part => part.startsWith('.') || part.toLowerCase() === 'templates'));
    const generation = crypto.randomUUID();
    const manifest = {};
    const hashes = {};
    let count = 0;
    for (const file of files) {
      const markdown = await this.app.vault.read(file);
      for (const embed of core.findEmbeds(markdown)) {
        const base = this.app.metadataCache.getFirstLinkpathDest(embed.base, file.path);
        if (!base || base.extension !== 'base') throw new Error(`${file.path}: Base not found: ${embed.base}`);
        const definition = parseYaml(await this.app.vault.read(base));
        const config = core.selectView(definition, embed.view);
        const snapshot = await this.capture(config, file.path);
        const relative = 'generated/' + generation + '/' + path.basename(core.snapshotName(file.path, embed.key));
        await core.atomicWrite(path.join(directory, relative), snapshot);
        (manifest[file.path] ||= {})[embed.key] = relative;
        hashes[relative] = crypto.createHash('sha256').update(snapshot).digest('hex');
        count++;
      }
    }
    const after = await core.inputDigest(this.vaultRoot);
    if (before !== after) {
      const error = new Error('Notes changed during export; wait until editing pauses, then retry.');
      error.code = 'NOTES_CHANGED';
      throw error;
    }
    // Snapshots are immutable per generation. A failed run leaves the previous
    // manifest intact; consumers never see a half-written set of results.
    const manifestText = stringifyYaml(manifest);
    const manifestDigest = crypto.createHash("sha256").update(manifestText).digest("hex");
    const contentDigest = await core.inputDigest(this.vaultRoot, true);
    if (after !== await core.inputDigest(this.vaultRoot)) throw new Error('Notes changed during export; retry.');
    const state = { schema: 1, inputDigest: after, contentDigest, generation, manifestDigest, exportedAt: new Date().toISOString(), hashes };
    await core.atomicWrite(path.join(directory, 'state.json'), JSON.stringify(state, null, 2));
    await core.atomicWrite(manifestPath, manifestText);
    this.lastExport = { views: count, generation, inputDigest: after };
    return this.lastExport;
  }

  async capture(config, sourcePath) {
    const host = document.createElement('div');
    host.style.cssText = 'position:fixed;left:-10000px;top:0;width:1000px;visibility:hidden;pointer-events:none';
    document.body.appendChild(host);
    const component = new Component();
    component.load();
    let quietTimer;
    let timeout;
    const result = new Promise((resolve, reject) => {
      this.activeCapture = {
        reject,
        updated: view => {
          clearTimeout(quietTimer);
          quietTimer = setTimeout(() => {
            try { resolve(core.tableSnapshot(view, sourcePath)); }
            catch (error) { reject(error); }
          }, 250);
        },
      };
      timeout = setTimeout(() => reject(new Error(`${sourcePath}: Obsidian did not return Bases results within 15 seconds.`)), 15000);
    });
    // Attach an error handler immediately, including while render is pending.
    result.catch(() => {});
    try {
      await MarkdownRenderer.render(this.app, '```base\n' + stringifyYaml(config) + '\n```', host, sourcePath, component);
      return await result;
    } finally {
      clearTimeout(quietTimer);
      clearTimeout(timeout);
      this.activeCapture = null;
      component.unload();
      host.remove();
    }
  }
};
