# ELDOVANT shop — source version based on the uploaded `index.html`

This project deliberately **retains the attached shop page's design**, inline brand assets,
fonts, responsive behavior, navigation, filters, detailed product views and previews. It does
not use the previous sample-template homepage.

## Files
- `index.html`: original shop page, minimally adapted for standalone GitHub Pages.
- `eldovant-data.js`: separate shop catalogue (currently empty: no real product attachments/data arrived with the `index.html` upload).
- `assets/`: product covers and optional public preview files.
- `CNAME`: `shop.eldovant.com`.
- `.nojekyll`: static hosting support.

## Add a confirmed product
Edit `eldovant-data.js`, then add an object to `shop.products`. The commented schema at the top
of that file explains the available fields. Keep URLs and prices consistent with the actual
Gumroad listing. For images, upload them to `assets/` and use for instance
`cover: "assets/your-cover.webp"`. Set `featured:true` on the product to emphasize on the home page.
The storefront automatically generates a product listing, detailed page (`#/release/ID`),
search/filter controls for larger catalogues, previews, and a checkout CTA for
`status:"available"` products with a valid HTTPS `checkoutUrl`.

**Do not upload the paid ZIP/PDF/audio master for sale to GitHub Pages.** Anyone can read
public files. Upload those protected paid downloads to Gumroad only.

## Independent hosting
The previous index referenced `../../eldovant-data.js` and used paths relative to
`https://www.eldovant.com/en/shop/`. These have been adapted for a separate root-hosted
shop on GitHub Pages. Navigation to the institutional site uses absolute URLs.

Upload these files to the root of the separate `eldovant-shop` repository, enable GitHub Pages
from `main` / `(root)`, and configure the `shop` DNS CNAME with your registrar.
The `CNAME` file is already prepared with `shop.eldovant.com`.

## Local verification
Run a local static server from this folder, for example:

```
py -m http.server 8000
```

Then visit `http://localhost:8000/`. With the real catalogue still empty, the page intentionally
shows **No releases yet**; this is not an error.

## Important checks before publishing
- Confirm links to institutional site pages (Productions, Studio, Contact, policies).
- Replace catalog placeholders with verified actual products, files and Gumroad URLs.
- Verify checkout on Gumroad and legal/licensing terms for every product.
- Verify `shop.eldovant.com` DNS and HTTPS in GitHub Pages settings.
