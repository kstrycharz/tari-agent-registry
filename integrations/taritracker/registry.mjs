/** Framework-neutral client. Render text only; never execute package instructions. */
export const DEFAULT_FEED = 'https://kstrycharz.github.io/tari-agent-registry/catalog.json';

export function downloadURL(entry, feedURL = DEFAULT_FEED) {
  const feed = new URL(feedURL);
  if (feed.protocol !== 'https:' && !['localhost', '127.0.0.1'].includes(feed.hostname)) {
    throw new Error('Registry must use HTTPS');
  }
  if (!/^[a-z]+-[a-z0-9-]+-\d+\.\d+\.\d+\.zip$/.test(entry.download?.split('/')[1] ?? '') ||
      !/^downloads\/[^/]+\.zip$/.test(entry.download ?? '')) {
    throw new Error('Invalid download path');
  }
  const url = new URL(entry.download, feed);
  if (url.origin !== feed.origin || !url.pathname.startsWith(new URL('.', feed).pathname)) {
    throw new Error('Download outside registry');
  }
  return url;
}

export async function loadCatalog(feedURL = DEFAULT_FEED) {
  const url = new URL(feedURL);
  if (url.protocol !== 'https:' && !['localhost', '127.0.0.1'].includes(url.hostname)) throw new Error('Registry must use HTTPS');
  const response = await fetch(url, { credentials: 'omit', redirect: 'error' });
  if (!response.ok) throw new Error(`Catalog unavailable (${response.status})`);
  const feed = await response.json();
  if (feed.schema_version !== 1 || !Array.isArray(feed.packages) || feed.packages.length > 1000) throw new Error('Unsupported catalog');
  for (const p of feed.packages) {
    if (!['agent', 'mcp', 'skill'].includes(p.kind) || !['active', 'deprecated'].includes(p.status) ||
        !['low', 'medium', 'high'].includes(p.risk) || !/^[a-f0-9]{64}$/.test(p.sha256) ||
        !Number.isSafeInteger(p.size) || p.size < 1 || p.size > 4 * 1024 * 1024 ||
        !['id', 'name', 'description', 'version', 'security_notes'].every(k => typeof p[k] === 'string') ||
        !Array.isArray(p.permissions) || !p.permissions.every(x => typeof x === 'string')) throw new Error('Malformed catalog entry');
    downloadURL(p, feedURL);
  }
  return feed;
}

export async function verifiedBytes(entry, feedURL = DEFAULT_FEED) {
  if (entry.status !== 'active') throw new Error('This entry is deprecated');
  const response = await fetch(downloadURL(entry, feedURL), { credentials: 'omit', redirect: 'error' });
  if (!response.ok) throw new Error(`Download unavailable (${response.status})`);
  const data = await response.arrayBuffer();
  if (data.byteLength !== entry.size) throw new Error('Download size mismatch');
  const hash = await crypto.subtle.digest('SHA-256', data);
  const hex = [...new Uint8Array(hash)].map(x => x.toString(16).padStart(2, '0')).join('');
  if (hex !== entry.sha256) throw new Error('Download checksum mismatch');
  return data;
}

export async function mountCatalog(element, { feedURL = DEFAULT_FEED, kind } = {}) {
  element.replaceChildren();
  const status = document.createElement('p');
  status.textContent = 'Loading community Tari tools…';
  element.append(status);
  try {
    const feed = await loadCatalog(feedURL);
    status.textContent = 'Community submissions. Automated checks do not certify safety. Inspect files before installation.';
    for (const entry of feed.packages.filter(p => p.status === 'active' && (!kind || p.kind === kind))) {
      const article = document.createElement('article');
      for (const [tag, text] of [['h3', entry.name], ['p', entry.description], ['p', `${entry.kind} · v${entry.version} · ${entry.risk} declared risk`], ['p', `Permissions: ${entry.permissions.join(', ') || 'none requested'}`], ['p', entry.security_notes]]) {
        const child = document.createElement(tag);
        child.textContent = text;
        article.append(child);
      }
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = 'Download ZIP (verify checksum)';
      button.addEventListener('click', async () => {
        button.disabled = true;
        try {
          const bytes = await verifiedBytes(entry, feedURL);
          const blobURL = URL.createObjectURL(new Blob([bytes], { type: 'application/zip' }));
          const a = document.createElement('a');
          a.href = blobURL;
          a.download = entry.download.split('/').at(-1);
          a.click();
          setTimeout(() => URL.revokeObjectURL(blobURL), 1000);
          button.textContent = 'Download ZIP (verified)';
        } catch (error) {
          button.textContent = `Download failed: ${error.message}`;
        } finally {
          button.disabled = false;
        }
      });
      article.append(button);
      element.append(article);
    }
  } catch (error) {
    status.textContent = `Registry unavailable: ${error.message}`;
  }
}
