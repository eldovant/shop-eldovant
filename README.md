# ELDOVANT Shop — Free 5-minute Gumroad synchronization

**Purpose:** independent `eldovant-shop` GitHub repository, hosting the user-provided ELDOVANT HTML design with Cloudflare Pages, seller product management on Gumroad. The main `eldovant.com` site and its DNS apex remain untouched.

## Critical hosting note

GitHub Pages' documented terms disallow using that free hosting service to run a website primarily directed at facilitating e-commerce. **For the official commercial storefront**, use Cloudflare Pages as the static host, while retaining GitHub as the source repository and as the scheduled synchronization runner.

## 1. Create the dedicated Gumroad application

In the logged-in seller account: https://gumroad.com/settings/advanced → Applications → Create application.

- Application icon: optional ELDOVANT icon (PNG/JPG).
- Application name: `ELDOVANT Shop Sync`
- Redirect URI: `http://127.0.0.1`

Click `Create application`. On the subsequent edit page select **Generate access token**. The redirect URI is not used for an owner-only personal token (no website OAuth callback is involved). Do **not** delete or modify any existing `Gumroad Store Agent (internal)` application.

**Security:** Dashboard-generated personal tokens can carry broad account privileges, not guaranteed read-only scopes. Do not paste the token into code, chat, browser URL, commits or public files.

## 2. Configure GitHub

Use separate public repository `eldovant-shop` and upload all project files, including hidden `.github/workflows/sync-gumroad.yml`. We recommend GitHub Desktop or normal Git to preserve the hidden directory.

Repository → Settings → Secrets and variables → Actions → New repository secret:

- Name: `GUMROAD_ACCESS_TOKEN`
- Value: the token you generated privately in Gumroad.

Repository → Settings → Actions → General → Workflow permissions: ensure GitHub Actions has **Read and write permissions** (or the repository/org policies otherwise allow the explicit `contents: write` workflow permission).

Optionally set a repository variable `SHOP_REQUIRED_TAG` to `eldovant-shop` if the public catalogue should only include explicitly tagged products. Without the variable, the importer includes all eligible published digital products. An optional comma-separated `GUMROAD_EXCLUDE_IDS` variable can exclude specific product IDs.

Repository → Actions → `Sync Gumroad products every five minutes` → **Run workflow** → `main` → Run workflow.

### How the frequency works

GitHub Actions runs a *best-effort* cron every 5 minutes (at minutes 02,07,12,... UTC), its minimum supported interval. It only commits `eldovant-data.js` when the product data changes. Cloudflare Pages automatically publishes a new version when the repo receives that commit. No changes = no additional deployment. GitHub-hosted standard runners are free in PUBLIC repositories; note that GitHub can delay or skip scheduled runs and automatically disable public repository cron schedules after 60 days without repo activity.

## 3. Cloudflare Pages free static hosting

Cloudflare dashboard → Workers & Pages → Create application → Pages → Connect to Git / Import existing Git repository → select `eldovant-shop`.

- Production branch: `main`
- Framework preset: None
- Build command: `sh build.sh`
- Build output directory: `dist`

Cloudflare Pages has a Free plan which currently includes 500 builds per month. Because this repo only commits on actual product changes, the GitHub job's 5-minute polling does **not** use up 288 Cloudflare builds per day.

Cloudflare Pages → project → Custom domains → Set up a custom domain → `shop.eldovant.com`.

If `eldovant.com` DNS remains managed at Register.it (as intended), only change the existing `shop` CNAME **after** Cloudflare shows the target for its project, typically:

- TYPE: `CNAME`
- HOST: `shop`
- TARGET: `<your-cloudflare-project>.pages.dev` (replace with actual project domain)

Do NOT change nameservers, apex `@`, `www`, MX, SPF, DKIM or DMARC. Enable HTTPS / wait for certificate after custom domain activation. No new domain purchase required. Remove the obsolete GitHub Pages custom-domain setting when you complete migration to prevent confusion.

## 4. Product management

Create/modify/publish on Gumroad. At the next successful synchronization GitHub Actions fetches `GET https://api.gumroad.com/v2/products` with the token in an Authorization header; filters ineligible products; writes only a safe whitelist of customer-facing fields to `eldovant-data.js`. Gumroad remains responsible for product checkout, payments and digital delivery.

- Base price, title, summary, image, product URL and simple category/tag are imported.
- Variable/personalized pricing, tax and discount amounts must be confirmed in Gumroad checkout.
- A product's publication is not instant: scheduled job + Git commit + Cloudflare deployment and caches can add latency.
- The special Gumroad-only injected `gumroad-data`/`gumroad-prices`/follow attributes are **not** available on this external host; this project uses the API importer instead.

## 5. Project structure

```text
index.html                        # original provided ELDOVANT shop design
eldovant-data.js                  # generated/public catalogue; initial empty fallback
build.sh                          # static deployment selection
scripts/sync_gumroad.py           # API importer; private token never exported
.github/workflows/sync-gumroad.yml  # 5-minute scheduler
README.md
tests/
```

**Test offline:** `python -m unittest discover -s tests -v`, `sh build.sh`.

**No automated Gumroad API access has been configured by this ZIP alone.** Account owner must create and authorize the app, store token on GitHub, and connect the repository to hosting.
