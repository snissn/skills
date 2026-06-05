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

## Deck Design Contract

This contract is mandatory for deck-wide polish work. Treat deviations as defects unless a slide uses a named exception template.

1. Slide frame
   - Marp slide size is 16:9 at 1280 x 720.
   - Use one canonical frame: left 76px, right 76px, top 52px, and a reserved footer safe area of at least 104px.
   - Normal slide content starts from the shared content frame. Primary text anchors to the same left edge; content may not enter the footer/page-number band.
   - Allowed frame exceptions: cover, intentionally full-bleed visual slides, section dividers, and the closing ask slide. Exceptions must still preserve shared chrome and footer-safe behavior.
   - Cover slides use a named `.cover` / `.title-slide` contract, not normal slide footer-safe rules. Covers may opt out of standard footer text, footer rail, page-number divider, and page number, but must keep intentional margins, subtle decorative chrome, and a stable hero composition.
   - Cover hero layout should be a deliberate two-column central band: left visual, right title/copy stack, image center and text-block center optically aligned with a slight upward bias. Do not let cover content drift toward the footer band.

2. Eyebrow / section label
   - All top section labels use one canonical eyebrow component: left offset 76px, top offset 82px, rail width 26px, rail height 2px, 10px gap to text.
   - Typography: uppercase, 13px, 820-860 weight, 0.12em letter spacing, 1.1 line height.
   - Default color is muted deck text; accent color may only come from a slide semantic variable such as `--eyebrow-color`.
   - No one-off manually positioned labels. If a slide needs a different label treatment, create a named template and document the exception in CSS.
   - All slides should use the same `.eyebrow` structure or a direct semantic wrapper that inherits the same `.eyebrow` rules.

3. Titles
   - Normal slide H1/H2 titles start from the shared title block under the eyebrow.
   - Standard title size is 46px for normal slides, with line-height 1.03-1.06 and max width 900-1080px.
   - Compact technical or dense slides may use 40-42px only through a named template. Hero/cover slides may use larger title tokens.
   - Title margin below to lead/subhead is 14-18px. Do not use arbitrary per-slide title sizes or offsets.
   - Two-line titles should wrap intentionally inside the title max width; do not shrink text ad hoc unless the template defines compact mode.

4. Lead/subhead text
   - Lead/subhead text aligns to the same left edge as the title.
   - Standard lead width is 860-980px, font size 18-23px, line-height 1.25-1.34.
   - Standard margin from title to lead is 12-18px. Slide-specific lead positioning is allowed only inside a named template.

5. Main content frame
   - Cards, diagrams, panels, screenshots, and process rows begin from a shared content y-position after the lead, normally 24-34px below the lead.
   - Standard card gap is 14-20px. Standard panel radius is 6px. Standard panel border/background/shadow comes from shared card/panel tokens.
   - Use named primitives for 3-card grids, 4-card grids, 5-step process rows, two-column visual layouts, marketplace cards, and dense technical diagrams.
   - Common content should not use per-slide margin hacks. If several slides need similar placement, create a shared primitive.

6. Footer zone
   - Every normal slide reserves the same bottom band for footer text, page number, and optional recap/callout.
   - Footer text position and page number position are identical across normal slides.
   - Bottom callout strips sit above the footer band and never collide with footer text or page numbers.
   - If no visible callout exists, the reserved bottom space still remains clear.
   - Do not use both a heavy bottom callout and a heavy footer/contact strip in the same vertical band.

7. Page numbers
   - Page numbers use one position: right 32px, bottom 20px, with the shared font size, weight, color, and divider treatment.
   - Cover behavior must be intentional and consistent with deck policy. Appendix labels only appear if an appendix section actually exists.
   - No page number drift or per-slide page-number selectors for normal slides.

8. Corner marks / chrome
   - Corner bracket positions and dimensions come from shared tokens: x 54px, y 52px, size 28px unless the base frame changes.
   - Chrome lives above backgrounds and below content where possible. Full-bleed visual layers must restore chrome through a shared foreground overlay or shared background token stack.
   - Do not hand-draw per-slide bracket variants. Do not allow image or overlay layers to obscure top-left or bottom-right chrome.

9. Callout / recap strips
   - Callouts are governed by template rules, not styling alone. A slide may use a bottom callout only when its content template explicitly reserves vertical room above the footer safe area.
   - Use three explicit variants:
     - `.callout-bottom-safe` for slides whose cards/diagrams are sized to leave a clear bottom-callout lane above the footer band.
     - `.callout-inline` for notes that belong inside the normal content flow below or beside panels.
     - `.callout-none` when the slide title/subtitle already makes the point or the slide is too dense for a recap.
   - Bottom callouts are opt-in. Do not make full-width bottom positioning the default shared behavior.
   - Standard style: 1px border, 3px accent left rail, 6px radius, quiet translucent background, 12-18px horizontal padding, 12-18px font depending on length.
   - Avoid repetitive labels such as `Bottom line:` unless the label carries semantic meaning.
   - Callouts must not overlap panels, cards, diagrams, chrome, footer text, or page numbers.
   - Do not use a full-width bottom callout on dense card slides unless the card grid is explicitly shortened or moved up to reserve room.

10. Cards
    - Cards use shared border, radius, background, shadow, inner padding, title size, body size, and accent rail/rule behavior.
    - Icons, when used, should have a shared size within each template. Cards in the same row must have equal height and aligned titles.
    - Use named 3-card, 4-card, and large-card layouts. Avoid nested cards unless part of a named technical diagram template.

11. Image and screenshot panels
    - Image panels use standard object-fit, border, radius, crop, opacity, and contrast rules for their template.
    - Dark/light image pairs must be wired and visually comparable. Light mode should not inherit unreadable dark screenshot opacity.
    - Screenshots must be readable enough to communicate product reality and must not obscure chrome, footer, or page number.

12. Light-mode parity
    - Base CSS owns layout. Light CSS should override color, contrast, image visibility, and light-only tuning only.
    - Do not duplicate layout rules in light mode unless a documented rendering difference requires it.
    - Compare dark and light outputs slide-by-slide before claiming completion.

13. Validation protocol
    - Build dark and light outputs before and after systemic changes.
    - Screenshot every slide in both modes for finalization work.
    - Produce a visual defect list before editing with slide number, mode, element, defect, root cause, and systemic fix.
    - After editing, produce a defect-resolution summary. Successful build alone is not validation.

14. Anti-patterns
    - Forbidden: one-off per-slide margin hacks for common elements, manually positioned eyebrows, custom footer bars per slide, arbitrary H1 scale overrides, content bleeding into the footer safe area, duplicate light-mode layout rules, stale appendix/page-label selectors, generated output hand-edits, and slide-specific chrome variants outside shared primitives.

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
   - Narrative order: when slides are reordered, compare the rendered sequence against the intended story arc, not just the source order. Check that moved slides no longer carry stale appendix labels, appendix class names, old speaker-note framing, or page-number exceptions from their previous location.
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
- Reordered slides have been visually checked against the intended story sequence, and moved main-deck slides do not retain stale appendix/source-position naming or notes.
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
