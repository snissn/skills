---
name: polystore-deck-polish
description: Polish the PolyStore Marp investor deck so it feels finalized and visually consistent across all slides, including page numbers, footer elements, title sizing, shared layout templates, dry CSS, and high-quality dark/light image elements. Use when working in /home/mikers/dev/polynomialstore/deck or its theme folder, especially for deck-wide UI consistency, visual refinement, Marp theme refactors, dark/light parity, or final presentation QA.
---

# PolyStore Deck Polish

Use this skill for final-pass design, consistency, and maintainability work on the PolyStore deck at `/home/mikers/dev/polynomialstore/deck`.

## Scope

Primary files:

- `slides.md` - Marp slide source and per-slide classes.
- `theme/polystore.css` - shared dark theme and base layout system.
- `theme/polystore-light.css` - light-mode overrides only.
- `assets/` - paired dark/light raster images, icons, diagrams, and brand assets.
- `package.json` - render/export commands.

Generated files in `dist/` are build outputs. Regenerate them when validating or when the user asks for final artifacts.

## Operating Principles

- Treat this as a deck system, not isolated slide styling. Prefer shared classes, tokens, and layout primitives when they fix visible drift across multiple slides.
- Keep `polystore.css` as the source of structure and component behavior. Keep `polystore-light.css` focused on color, contrast, image visibility, and light-specific tuning.
- Preserve Marp compatibility. Respect frontmatter and slide directives such as `paginate`, `footer`, `_class`, and `_paginate`; do not introduce app-only runtime dependencies for a static deck.
- Keep the design restrained and investor-grade: dense enough to scan, minimal text, polished diagrams, no decorative clutter.
- Keep light and dark modes as equal first-class outputs. Every visual treatment must work in both.
- Do not invent missing business facts. Leave raise, traction, team, benchmark, audit, provider, or roadmap placeholders intact unless the user gives real inputs.

## Workflow

1. Inspect the deck structure:
   - Read `slides.md`, `theme/polystore.css`, `theme/polystore-light.css`, and `package.json`.
   - Identify slide classes, repeated patterns, asset pairs, title/subhead variations, footer and pagination behavior.
   - Check `git status --short` before editing and preserve unrelated user changes.

2. Build and visually audit before deciding on edits:
   - Run `npm run build:all` unless dependencies are missing.
   - Open or screenshot both `dist/polystore-accountable-retrieval.html` and `dist/polystore-accountable-retrieval-light.html`.
   - Review every slide in both modes when doing a finalization pass, comparing dark and light versions slide-by-slide for parity. For a narrower request, review the target slides plus cover, a normal text slide, an image-heavy slide, and appendix treatment.
   - Compare repeated deck chrome and footer-zone elements by eye across adjacent screenshots: corner marks, header/eyebrow rails, title anchor points, footer, page number, appendix/section labels, bottom recap/callout strips, and any persistent brand elements.
   - For full-bleed image, hero, or visual-background slides, verify persistent chrome is still visible above the image/overlay layer. Do not assume section-level background chrome is visible when an absolute visual layer covers the section.
   - Compare the main content bounding box across non-cover slides: top anchor, left/right margins, bottom clearance above the footer zone, and whether slide-specific content starts from the shared template position.
   - Record concrete visual defects before editing: slide number, mode, affected element, and proposed fix.
   - Do not treat successful HTML/PDF generation as visual proof.

3. Audit consistency against the visual evidence:
   - Page chrome: top-left/top-right corner brackets, background grid/corner ornaments, footer rails, page numbers, appendix/section labels, and brand marks should share stable positions, sizes, and visibility rules across slides unless a slide class explicitly opts out.
   - Chrome layering: full-bleed image panels, visual overlays, and absolute background elements must not hide required brackets, page numbers, footer rails, or brand marks. Move chrome to a shared foreground layer or replicate it through a shared overlay primitive when the section background is covered.
   - Page numbers: position, color, weight, visibility, cover treatment, appendix treatment.
   - Appendix/section labels: main-flow slides should use the normal deck page label. Appendix or custom section labels must match the current deck structure and should not remain after a slide is moved back into the main flow.
   - Footer zone: footer, page number, corner marks, appendix/section labels, and any bottom recap/callout strip must have a shared layout contract with clear vertical separation and no crowding. Reserve this band even when a particular slide has no visible footer text, page number, or recap strip; main content should not bleed into the space where deck chrome normally lives.
   - Footer: position, text weight, color, relationship to page number, cover behavior.
   - Recap/callout strips: use one shared component family for bottom takeaways. Avoid repeated literal boilerplate such as `Bottom line:` on every slide; prefer a short recap phrase, or omit the strip when it restates the slide title or thesis.
   - Titles: h1/h2 scale, line-height, max width, top/left anchor, class-specific overrides, compact headers.
   - Slide headers: eyebrow spacing, rail length, subhead width, vertical rhythm, and distance from the slide edges.
   - Main content templates: except for the cover and intentionally full-bleed/hero slides, primary content should start from a shared content frame with stable top, left, right, and bottom safe-area tokens. Slide-specific classes may change internal layout, but they should not redefine the deck's main content anchor without a clear reason.
   - Components: cards, callouts, metric rows, process steps, diagrams, side panels, source notes.
   - Assets: dark/light pair availability, crop, opacity, contrast, object-fit, visual quality, and whether the image is integral rather than decorative.
   - Marp behavior: global `paginate` and `footer`, cover conventions, and any per-slide `_paginate` exceptions.
   - Dead chrome rules: remove unused legacy selectors for old page labels, footer variants, or recap styles once the slide source no longer uses them. Do not leave stale appendix/page-label primitives that could be accidentally reintroduced.

4. Refactor only when duplication is causing visible drift:
   - Add or consolidate shared tokens in `:root`.
   - Create reusable layout primitives for repeated page chrome, reserved footer zones, headers, footers, recap/callout strips, main content frames, cards, panels, figure/image slots, source notes, and two-column/stacked compositions.
   - When full-bleed templates need persistent chrome, use a shared foreground chrome overlay or shared overlay background tokens rather than per-slide hand-drawn brackets.
   - If content alignment differs across many slides, introduce or strengthen standard templates before tuning individual slides: for example base content frame, title-and-grid, title-and-visual, full-bleed image, appendix, and contact/closing layouts.
   - Replace near-duplicate per-slide rules with component classes when it reduces real drift.
   - Keep slide-specific classes only for semantic layout differences.
   - Prefer shared tokens for margins, corner/chrome offsets, header anchors, title scale, footer/pagination, panel treatment, or figure slots over a broad CSS rewrite.
   - Do not make a broad rename unless it clearly improves maintainability and all references are updated.

5. Polish slides systematically:
   - Normalize title sizing and header rhythm before tuning individual slide internals.
   - Normalize persistent page chrome before slide-specific composition: corner brackets, decorative corner marks, header/eyebrow rails, footer, page number, and appendix label should align to the same tokenized offsets.
   - Check chrome after all full-bleed imagery and overlay masks are applied; if a visual layer covers the section background, restore the chrome in that template's foreground overlay.
   - Establish a reserved bottom safe area before placing diagrams, legends, cards, or callouts. Content may approach the footer zone only through an intentional shared component that accounts for the footer and page number.
   - Normalize non-cover main content to a shared content frame before local layout tweaks. Preserve exceptions only for intentionally full-bleed visual slides, cover/title slides, or slides with a documented alternate template.
   - Decide the deck-wide recap convention before styling individual takeaways: use concise unlabeled recap phrases, use a named label only when it carries meaning, or remove the recap strip when the footer alone is cleaner.
   - Align recurring elements to shared margins and grid positions.
   - Make every image/diagram feel designed: stable dimensions, intentional crop, consistent border/radius/shadow rules, accessible contrast, and matching dark/light variants.
   - Use existing paired assets first. Use the `imagegen` skill/tool only when a missing or low-quality raster visual is the blocker after auditing existing assets, then wire the result into both themes.
   - Prefer SVG or CSS for crisp diagrams when the deck already uses those patterns; prefer raster images for atmospheric or product-like visual panels.
   - Avoid nested cards, oversized hero type inside compact panels, one-off decorative blobs, and text that can overlap or overflow.

6. Validate both modes:
   - Run `npm run build:all` after edits.
   - For final deck passes, run `npm run pdf`, `npm run pdf:light`, `npm run pptx`, and `npm run pptx:light`. For narrow theme iterations, HTML validation may be enough if the user did not ask for final artifacts.
   - Re-open or screenshot the dark and light outputs. For finalization passes, verify every slide in paired dark/light comparison; for narrower changes, verify every touched slide plus representative unaffected slides.
   - Check cover, thesis/problem, image-heavy slides, technical diagrams, economics/metrics, status/ask, and appendix.
   - Fix visible drift rather than describing it.

## Design Checklist

Before finishing, confirm:

- Pagination and footer have the same visual system across normal slides, cover, and appendix.
- Slides reserve the footer/page-number safe area even when a footer element is hidden or intentionally omitted.
- Decorative page chrome, especially corner brackets and header/eyebrow rails, has consistent offsets, scale, and visibility across slides and modes.
- Full-bleed visual slides do not hide persistent chrome behind image or overlay layers.
- Marp pagination/footer directives still behave intentionally, including any `_paginate` exceptions.
- Main-flow slides use normal page numbers; appendix/section labels only appear where the deck structure actually calls for them.
- No unused legacy appendix/page-label or footer selectors remain after migrating to the shared chrome system.
- Bottom recap/callout strips follow one style and content convention, avoid boilerplate labels repeated slide after slide, and never intrude into the footer/page-number zone.
- Header blocks use consistent title sizes, top/left anchors, subhead spacing, and eyebrow treatment.
- Main content on non-cover slides uses a standard content frame or a named alternate template; cards, legends, diagrams, and captions do not drift into the footer zone.
- Light theme overrides do not duplicate base layout rules except when genuinely necessary.
- Repeated components use shared selectors and tokens.
- Every slide has a designed visual hierarchy: primary message first, support second, sources/notes quiet.
- Image panels and icons are consistently sized, aligned, and tuned for both dark and light modes.
- Source footnotes are readable but visually subordinate.
- No text overlaps, clips, or crowds the footer/page number.
- Generated artifacts build successfully and visual review was performed, or any unavailable tool is reported explicitly.

## Commands

From `/home/mikers/dev/polynomialstore/deck`:

```bash
npm run build:all
npm run pdf
npm run pdf:light
npm run pptx
npm run pptx:light
```

Use focused commands during iteration, then run the broader set for final delivery.
