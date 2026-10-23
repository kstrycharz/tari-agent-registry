# Serving downloads on taritracker.com

The registry publishes these static assets on GitHub Pages:

```
https://kstrycharz.github.io/tari-agent-registry/catalog.json
https://kstrycharz.github.io/tari-agent-registry/SHA256SUMS
https://kstrycharz.github.io/tari-agent-registry/downloads/skill-tari-development-1.0.0.zip
```

The website source is a separate project. Copy `integrations/taritracker/registry.mjs`
into that project and mount it wherever skills should be listed:

```html
<section aria-label="Tari community skills" id="tari-skills"></section>
<script type="module">
  import { mountCatalog } from '/assets/registry.mjs';
  mountCatalog(document.querySelector('#tari-skills'), { kind: 'skill' });
</script>
```

Omit kind to show all entries, or use `agent` / `mcp`. Adapt the DOM renderer to
the existing site's styling/framework. The client uses textContent, checks URL
boundaries, hides deprecated entries, displays permissions and verifies bytes
with Web Crypto before offering the ZIP. It never installs or executes a package.
Checksum verification protects against corruption, not a compromised catalog.

GitHub Pages permits cross-origin static fetches. If the site has a restrictive
Content Security Policy, allow `https://kstrycharz.github.io` in connect-src and
allow blob downloads. A restrictive sandbox may also require allow-downloads.
If you want every download served directly from taritracker.com, mirror the
**whole** dist tree under `/registry/` during the site's existing deployment:

```js
mountCatalog(document.querySelector('#tari-skills'), {
  kind: 'skill',
  feedURL: 'https://taritracker.com/registry/catalog.json'
});
```

Preserve relative paths. Publish catalog and ZIPs atomically, serve JSON as
application/json and ZIPs as application/zip, and keep catalog cache short.
Do not commit generated dist to this repository or fetch unreviewed PR artifacts
into the production website. Display publisher/revision if adding provenance UI.

For local integration tests, build into a fresh output directory, serve it with
`python -m http.server --directory dist 8000`, and set feedURL to
`http://localhost:8000/catalog.json`. The web page itself must use a secure context
(HTTPS or localhost) for Web Crypto. Test with the production site's CSP before launch.
