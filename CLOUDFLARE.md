# Cloudflare deployment

Upstream LibreTV 2.20.2; deployment branch: `deploy/cloudflare`.

- Website: https://tv.wydns.dpdns.org
- Worker: `libretv` (Cloudflare Workers, not Pages)
- Keep upstream `main` separate. Review and test upstream merges before publishing.
- No paid products, R2, KV, D1 or automatic upstream synchronization were enabled.

## Build and publish

Node.js 22:

```sh
npm ci
npm test
npm run build:cloudflare
npx wrangler deploy --secrets-file .dev.vars --strict
python3 scripts/check-deployment.py https://tv.wydns.dpdns.org
```

The local `.dev.vars` file contains `PASSWORD`, `PROXY_SECRET`, and `COOKIE_SECURE=true`. It is ignored by Git and must never be committed. Cloudflare stores these values as Worker secrets. Existing secrets survive later deployments.

No GitHub-to-Cloudflare automatic deployment is configured. The repository preserves the exact deployment source; publishing is currently explicit through Wrangler.

The application does not bundle content sources. Configure only sources you have permission to use. History and settings live in each browser, not a shared server database.

## Checks and constraints

504 upstream unit tests and a Workers-runtime smoke check cover login, protected APIs, private-address rejection, and fetching/rewriting a public HLS test playlist. This is not an end-to-end guarantee for arbitrary content sources or long IPTV sessions.

Workers Free has CPU, daily request and subrequest limits. Proxying media creates many requests. Monitor usage; do not enable a paid plan without approval. In-memory caches and login throttles are per isolate, not globally shared.
