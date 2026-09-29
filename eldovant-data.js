/*
 ELDOVANT Shop — standalone catalog for https://shop.eldovant.com/
 This file is intentionally separate from the main ELDOVANT website.
 Publish ONLY confirmed products. No commercial product data was present in
 the uploaded index.html; add your actual products to the `products` array.

 Example (COMMENT ONLY; not published):
 {
   id: "your-real-product-id",              // unique URL-friendly identifier
   title: "Your confirmed product title",
   summary: "One concise description.",
   description: "Long paragraph.\\n\\nAnother paragraph.",
   category: "Cinematic Assets",
   kind: "Digital download",
   year: "2026",
   featured: true,                         // optional: featured homepage release
   status: "available",                    // available | soon | unavailable
   cover: "assets/real-product-cover.webp", // optional; upload this image to assets/
   imageAlt: "Description of product artwork",
   ratio: "4/5",
   price: { amount: 19, currency: "EUR" },  // actual price, not cents
   format: "ZIP",
   size: "120 MB",
   includes: ["Item A", "Item B"],
   licence: "Use terms applicable to the purchased item",
   checkoutUrl: "https://eldovant.gumroad.com/l/REAL-PRODUCT-SLUG", // valid HTTPS URL only
   previews: [
     { type: "audio", src: "assets/preview.mp3", title: "Sample" },
     { type: "youtube", id: "VALID_VIDEO_ID", title: "Trailer" },
     { type: "file", src: "assets/preview.mp4", title: "Preview" }
   ],
   related: ["another-product-id"]
 }

 For pre-release listing use status:"soon" and omit checkoutUrl.
 Never place the paid download file itself in a public GitHub Pages repository.
*/
window.ELDOVANT_DATA = {
  contact: { email: "contact@eldovant.com" },
  entity: "ELDOVANT",
  social: [
    { name: "YouTube", href: "https://www.youtube.com/@eldovant" },
    { name: "Instagram", href: "https://www.instagram.com/eldovant/" },
    { name: "TikTok", href: "https://www.tiktok.com/@eldovant" }
  ],
  shop: {
    enabled: true,
    provider: "Gumroad",
    supportEmail: "contact@eldovant.com",
    delivery: {
      method: "Digital delivery through Gumroad",
      after: "Gumroad provides access or download details following a successful purchase."
    },
    products: [
      // Insert attached/verified product records here. No product records were supplied with index.html.
    ]
  }
};
