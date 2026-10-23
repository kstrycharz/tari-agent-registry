import test from 'node:test';
import assert from 'node:assert/strict';
import { downloadURL, loadCatalog, verifiedBytes } from './registry.mjs';

test('download paths stay under the registry origin and prefix', () => {
  const feed = 'https://example.com/registry/catalog.json';
  assert.equal(downloadURL({ download: 'downloads/skill-example-1.0.0.zip' }, feed).href, 'https://example.com/registry/downloads/skill-example-1.0.0.zip');
  for (const download of ['//evil.example/x.zip', '../x.zip', 'downloads/../x.zip', 'https://evil.example/a.zip', 'downloads/a.zip?x=1', 'downloads/a/b.zip']) {
    assert.throws(() => downloadURL({ download }, feed));
  }
  assert.throws(() => downloadURL({ download: 'downloads/skill-example-1.0.0.zip' }, 'http://example.com/catalog.json'));
});

test('verified downloads reject corrupt bytes and deprecated entries', async () => {
  const original = globalThis.fetch;
  const data = new TextEncoder().encode('example zip bytes');
  const sha256 = Buffer.from(await crypto.subtle.digest('SHA-256', data)).toString('hex');
  const entry = { download: 'downloads/skill-example-1.0.0.zip', status: 'active', size: data.length, sha256 };
  try {
    globalThis.fetch = async () => new Response(data);
    assert.equal((await verifiedBytes(entry)).byteLength, data.length);
    await assert.rejects(verifiedBytes({ ...entry, sha256: '0'.repeat(64) }), /checksum/);
    await assert.rejects(verifiedBytes({ ...entry, size: 1 }), /size/);
    await assert.rejects(verifiedBytes({ ...entry, status: 'deprecated' }), /deprecated/);
  } finally {
    globalThis.fetch = original;
  }
});

test('malformed catalogs fail closed', async () => {
  const original = globalThis.fetch;
  try {
    globalThis.fetch = async () => new Response(JSON.stringify({ schema_version: 2, packages: [] }));
    await assert.rejects(loadCatalog(), /Unsupported/);
    globalThis.fetch = async () => new Response(JSON.stringify({ schema_version: 1, packages: [{}] }));
    await assert.rejects(loadCatalog(), /Malformed/);
    globalThis.fetch = async () => new Response('', { status: 503 });
    await assert.rejects(loadCatalog(), /503/);
  } finally {
    globalThis.fetch = original;
  }
});
