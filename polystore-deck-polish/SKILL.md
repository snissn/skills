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

### Color Role Contract

Color use is semantic, not decorative. Each deck mode has a primary and secondary accent, and recurring components must consume those roles through tokens rather than hard-coded cyan/pink choices.

1. Accent roles
   - Dark mode primary accent is the deck pink; secondary accent is the deck cyan.
   - Light mode primary accent is the deck cyan; secondary accent is the deck pink.
   - Keep the approved cyan and pink hues unless the user explicitly asks for a palette change. Swap only their roles between modes.
   - Define and use shared tokens such as `--primary-accent`, `--secondary-accent`, and mode-safe accent wash/border tokens. Do not rely on class names like `.cyan` or `.pink` as the source of semantic priority.

2. Required primary uses
   - Eyebrow rail/highlight uses the primary accent. Eyebrow text remains neutral/soft for readability and should not be full primary-accent color unless the user explicitly requests a special title treatment.
   - Normal slide titles remain neutral title text, matching the approved dark/light readable title treatment. Do not make normal slide titles fully primary-accent colored; reserve primary accent for nearby rails, footer elements, callout rails, and main message highlights.
   - Footer rail/highlight and bottom recap/callout left rail use the primary accent. Footer text and page numbers remain neutral/soft for readability unless the user explicitly requests a special emphasis treatment.
   - Main message elements such as thesis strips, bottom takeaways, closing contact bars, and principal card rails use the primary accent.

3. Secondary uses
   - Secondary accent is for supporting contrast inside main content: alternate routes, comparison states, minor nodes, and visual affordances where the primary point remains clear.
   - A slide should not feel like a rainbow. Use primary first, secondary sparingly, and reserve green/yellow/violet for semantic statuses only when the story needs them.
   - When a component row is meant to feel unified, all cards in that row should share the primary-accent treatment rather than each card using a separate hue.

4. Light/dark parity
   - Base layout and component geometry stay in `polystore.css`.
   - Light mode may override accent-role tokens and contrast values, but should not duplicate layout rules to change color hierarchy.
   - The light cover slide must render as a light-mode cover, including the light logo/visual and light background treatment.

5. Regression checks
   - Before finishing, scan both theme files for hard-coded cyan/pink values in recurring components. Replace them with role tokens unless they are intentionally defining the palette or a documented secondary detail.
   - Check every slide for a clear primary/secondary hierarchy in both modes: header/title/footer primary; supporting content either primary or secondary by design.

1. Slide frame
   - Marp slide size is 16:9 at 1280 x 720.
   - Use one canonical frame: left 76px, right 76px, top 52px, and a reserved footer safe area of at least 104px.
   - Normal slide content starts from the shared content frame. Primary text anchors to the same left edge; content may not enter the footer/page-number band.
   - Allowed frame exceptions: cover, intentionally full-bleed visual slides, section dividers, and the closing ask slide. Exceptions must still preserve shared chrome and footer-safe behavior.
   - Cover slides use a named `.cover` / `.title-slide` contract, not normal slide footer-safe rules. Covers may opt out of standard footer text, footer rail, page-number divider, and page number, but must keep intentional margins, subtle decorative chrome, and a stable hero composition.
   - Cover hero layout should be a deliberate two-column central band: left visual, right title/copy stack, image center and text-block center optically aligned with a slight upward bias. Do not let cover content drift toward the footer band.

2. Named layout templates
   - Template contracts are the source of truth. Slide numbers are only temporary examples from a current render and must not become permanent policy.
   - Every non-cover slide must be assigned to a named template before polishing. If the existing classes are inconsistent, infer the template from the rendered structure and then consolidate toward shared classes or tokens.
   - Current template families:
     - `normal-header`: standard non-cover slide with eyebrow, title, optional subhead, and one main content region.
     - `visual-header`: full-bleed or image-backed slide that still uses the normal header anchor and shared chrome.
     - `dense-technical`: compact technical or diagram slide with a smaller content gap and stricter fit budget.
     - `market-grid`: metric/card-heavy slide with reserved source-note, card-grid, and bottom-callout lanes.
     - `process-row`: lifecycle/process slide with fixed horizontal steps and a reserved bottom callout lane.
     - `closing-ask`: closing/ask slide. It may have distinct content composition, but its header/chrome rules must be explicitly declared.
     - `cover`: title slide with cover-specific composition and no normal footer/page-number obligations.
   - Do not validate against a preferred slide number. Validate against the active template reference: the canonical CSS variables, shared class, and measured artifact boxes for that template.
   - If a slide needs behavior outside a template, name the exception, document why it exists, and keep the exception local to that template rather than changing the primitive component.

3. Template audit before polish
   - Before editing a layout pass, create a quick template map: slide id/order, current class list, inferred template, header container, main content container, callout/footer behavior, and obvious drift.
   - Identify whether defects are template defects or content defects. Fix template defects first; content tuning comes after the template frame is stable.
   - Do not rely on the current slide order for semantic identity. If slides are reordered, regenerate the template map and revalidate template assignments.
   - Do not use thumbnails as proof of alignment. Contact sheets are only navigation aids. Layout claims require full-size screenshots, rasterized final PDFs, or measured bounding boxes.

### Eyebrow / Section Label Contract

Normal slide section labels are a controlled deck primitive. Treat any drift in label markup, tracking, rail geometry, or export text extraction as a regression.

1. Canonical component
   - All normal slides must use the single canonical `.eyebrow` component.
   - Do not add slide-specific eyebrow classes, inline styles, manual label positioning, or custom label color rules for normal slides.
   - Do not use split-span, dual-accent, or partially colored label markup unless the user explicitly approves a named special template for that slide.
   - Cover slides may opt out of the normal eyebrow component and use cover-specific chrome.

2. Required tokens
   - The base theme must define and use `--eyebrow-rail-w`, `--eyebrow-rail-h`, `--eyebrow-gap`, `--eyebrow-font-size`, `--eyebrow-letter-spacing`, `--eyebrow-color`, and `--eyebrow-rail-color`.
   - Eyebrow rail length, rail thickness, rail/text gap, font size, tracking, label color, and rail color must come from those tokens rather than per-slide values.

3. Typography rules
   - Labels are rendered with CSS `text-transform: uppercase`; do not hand-type labels with spaces between letters.
   - Use moderate tracking only. Current approved `--eyebrow-letter-spacing` is `0.055em` unless deliberately changed after dark/light visual QA and PDF/PPTX export checks.
   - Do not use extreme `letter-spacing`. Keep `word-spacing: normal`.
   - Labels must remain readable as normal words in rendered slides and extracted output. They must not appear as broken strings such as `THE S I S`, `L IVE TE STNET`, `POLYF S TECHN ICAL PROOF`, or `TECHN ICAL MOAT + ECONOM IC S`.

4. Geometry rules
   - Normal-slide eyebrows use the same top offset, left offset, rail position, rail length, rail thickness, rail/text gap, and text baseline.
   - No arbitrary per-slide margin overrides for normal-slide eyebrows. If a template needs a different header composition, document it as a named template and keep the `.eyebrow` primitive itself unchanged.
   - The active `normal-header` reference must come from template variables/classes, not slide numbers. For the current Marp PDF plus Ghostscript export path, the observed rendered reference is rail y-position `81px`, x-range `77-101px` at 96 DPI rasterization. Treat this as an artifact measurement of the current template, not as permanent design policy.
   - If a template drifts in the PPTX/PDF export even though HTML looks aligned, use a named export-compatibility shim on the template container, such as shared `--header-y-correction`. Do not add inline styles, move the `.eyebrow` primitive itself, or use correction variables as a substitute for consolidating the template.
   - Long labels such as `MARKET + COMPETITIVE LANDSCAPE`, `TECHNICAL MOAT + ECONOMICS`, and `CURRENT PHASE / ASK` should fit on one line without clipping, awkward wrapping, or manual spacing.

5. Dark/light parity
   - Eyebrow geometry lives in `theme/polystore.css`.
   - `theme/polystore-light.css` may only override eyebrow color or contrast.
   - Do not duplicate eyebrow layout rules in light mode unless a documented rendering bug requires it.

6. Regression checks
   - Build dark and light outputs.
   - For all final layout claims, inspect full-size pages or measured raster output. Do not use thumbnails or contact sheets as proof.
   - Screenshot/rasterize every non-cover slide in both modes and verify all normal-slide eyebrows align to the active template reference.
   - For PDF/PPTX export work, rasterize the final PDFs at a fixed DPI, currently 96 DPI, and compare eyebrow rail boxes for every slide assigned to the same template. The current `normal-header` rail reference measures `y=81`, `x=77-101`; remeasure this reference when the template changes.
   - Run text extraction checks for broken-label patterns against Marp HTML and any selectable-text PDF artifacts. The default PDF path is the mobile-safe PPTX/LibreOffice export because direct Marp and Marp/Ghostscript PDFs have rendered slowly on iPhone with this theme.
   - Confirm these labels extract as normal words: `THESIS`, `LIVE TESTNET`, `POLYFS TECHNICAL PROOF`, `TECHNICAL MOAT + ECONOMICS`, and `CURRENT PHASE / ASK`.

7. Anti-patterns
   - Forbidden: per-slide eyebrow margin hacks, hand-spaced labels, split-span labels for normal slides, dual-accent eyebrow labels in normal flow, stale `.section-label` selectors, stale `.dual-accent` eyebrow selectors, PolyFS-specific eyebrow margin overrides, and ask-slide eyebrow color overrides.

### Header / Title Contract

The header is a template primitive, not loose slide content. Eyebrow, title, and subhead geometry must be owned by shared header variables and template classes.

1. Header primitive
   - Prefer a canonical header container such as `.slide-header` plus a template modifier. Existing semantic wrappers such as `.market-system-header`, `.landscape-copy`, and `.ask-hero` may remain only if they are bound to the same template variables.
   - Required header tokens should include header x/y, title gap, title size, title line-height, title max width, and subhead gap/width. Current CSS may use `--normal-title-size`, `--normal-title-line`, `--normal-title-gap`, and related tokens; extend this token set rather than adding local offsets.
   - Template-specific wrappers may change internal max-width or content composition, but they may not redefine the normal header anchor unless they are a named exception template.

2. Titles
   - Normal slide H1/H2 titles start from the shared title block under the eyebrow.
   - Standard title size is 46px for normal slides, with line-height 1.03-1.06 and max width 900-1080px.
   - Compact technical or dense slides may use 40-42px only through a named template. Hero/cover slides may use larger title tokens.
   - Current deck convention: non-cover slides use the compact `normal-header` title system as the visual reference: shared upper-left frame, eyebrow at the same y-position, title 14px below the eyebrow, 40px title size, and line-height about 1.02. Use shared normal-title tokens for this instead of per-slide title offsets.
   - Title margin below to lead/subhead is 14-18px. Do not use arbitrary per-slide title sizes or offsets.
   - Two-line titles should wrap intentionally inside the title max width; do not shrink text ad hoc unless the template defines compact mode.
   - Do not vertically center a normal slide header with its content. Slides like thesis/statement and closing/ask must still anchor their eyebrow and title to the normal slide frame unless explicitly converted to a named cover/section-divider template.

3. Lead/subhead text
   - Lead/subhead text aligns to the same left edge as the title.
   - Standard lead width is 860-980px, font size 18-23px, line-height 1.25-1.34.
   - Standard margin from title to lead is 12-18px. Slide-specific lead positioning is allowed only inside a named template.

### Main Content Frame Contract

Main content failures are the same class of defect as eyebrow drift. Oversized cards, crowded diagrams, and callouts colliding with the footer are template defects until proven otherwise.

1. Content frame
   - Cards, diagrams, panels, screenshots, and process rows begin from a shared content y-position after the lead, normally 24-34px below the lead.
   - Standard card gap is 14-20px. Standard panel radius is 6px. Standard panel border/background/shadow comes from shared card/panel tokens.
   - Use named primitives for 3-card grids, 4-card grids, 5-step process rows, two-column visual layouts, marketplace cards, and dense technical diagrams.
   - Common content should not use per-slide margin hacks. If several slides need similar placement, create a shared primitive.
   - Main content may not enter the footer safe area. Reserve the footer/page-number/callout band even when visible footer elements are hidden or quiet.
   - Every template should declare the vertical budget for header, lead/subhead, main content, optional source notes, optional callout, and footer-safe area.

2. Fit and overflow rules
   - Treat text overflow, card crowding, diagram overlap, source-note collision, and content that feels too large/small as layout defects, not just copy issues.
   - Prefer fixing template sizing, grid tracks, fixed heights, line-height, content lanes, or max-widths before shrinking one slide ad hoc.
   - Cards in the same row must share stable height and aligned title/body baselines. A row should not change height because one card wraps differently unless the template intentionally supports that.
   - Dense diagrams must have explicit max-height, caption/source lanes, and footer clearance. If a diagram cannot fit, simplify the diagram or use a named dense template rather than squeezing global text.
   - Long source notes need a source-note lane with a defined font size and max lines. They must not push card grids or callouts into the footer band.

3. Footer zone
   - Every normal slide reserves the same bottom band for footer text, page number, and optional recap/callout.
   - Footer text position and page number position are identical across normal slides.
   - Bottom callout strips sit above the footer band and never collide with footer text or page numbers.
   - If no visible callout exists, the reserved bottom space still remains clear.
   - Do not use both a heavy bottom callout and a heavy footer/contact strip in the same vertical band.

4. Page numbers
   - Page numbers use one position: right 32px, bottom 20px, with the shared font size, weight, color, and divider treatment.
   - Cover behavior must be intentional and consistent with deck policy. Appendix labels only appear if an appendix section actually exists.
   - No page number drift or per-slide page-number selectors for normal slides.

5. Corner marks / chrome
   - Corner bracket positions and dimensions come from shared tokens: x 54px, y 52px, size 28px unless the base frame changes.
   - Chrome lives above backgrounds and below content where possible. Full-bleed visual layers must restore chrome through a shared foreground overlay or shared background token stack.
   - Do not hand-draw per-slide bracket variants. Do not allow image or overlay layers to obscure top-left or bottom-right chrome.

6. Callout / recap strips
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

7. Cards
    - Cards use shared border, radius, background, shadow, inner padding, title size, body size, and accent rail/rule behavior.
    - Icons, when used, should have a shared size within each template. Cards in the same row must have equal height and aligned titles.
    - Use named 3-card, 4-card, and large-card layouts. Avoid nested cards unless part of a named technical diagram template.

8. Image and screenshot panels
    - Image panels use standard object-fit, border, radius, crop, opacity, and contrast rules for their template.
    - Dark/light image pairs must be wired and visually comparable. Light mode should not inherit unreadable dark screenshot opacity.
    - Screenshots must be readable enough to communicate product reality and must not obscure chrome, footer, or page number.

9. Light-mode parity
    - Base CSS owns layout. Light CSS should override color, contrast, image visibility, and light-only tuning only.
    - Do not duplicate layout rules in light mode unless a documented rendering difference requires it.
    - Compare dark and light outputs slide-by-slide before claiming completion.

10. Validation protocol
    - Build dark and light outputs before and after systemic changes.
    - Screenshot or rasterize every slide in both modes for finalization work.
    - Produce a visual defect list before editing with slide order/id, template, mode, element, defect, root cause, and systemic fix.
    - Full-size page evidence is required for alignment, overflow, and hierarchy claims. Contact sheets may summarize results but cannot replace full-size review.
    - For template validation, measure bounding boxes where practical: header rail/title/subhead, main content top/bottom, card row heights, callout top/bottom, footer/page number.
    - After editing, produce a defect-resolution summary. Successful build alone is not validation.

11. Anti-patterns
    - Forbidden: one-off per-slide margin hacks for common elements, manually positioned eyebrows, slide-number-based design truth, thumbnail-only validation, custom footer bars per slide, arbitrary H1 scale overrides, content bleeding into the footer safe area, duplicate light-mode layout rules, stale appendix/page-label selectors, generated output hand-edits, and slide-specific chrome variants outside shared primitives.

## Workflow

1. Inspect the deck structure:
   - Read `slides.md`, `theme/polystore.css`, `theme/polystore-light.css`, and `package.json`.
   - Identify slide classes, repeated patterns, asset pairs, title/subhead variations, footer and pagination behavior.
   - Build a template map before making layout edits: slide order/id, classes, inferred template, header wrapper, main content wrapper, callout/footer behavior, and known exception status.
   - Identify template defects separately from content defects. If multiple slides drift in the same way, treat that as a template problem even when the slide source has different semantic class names.
   - Check `git status --short` before editing and preserve unrelated user changes.

2. Build and visually audit before deciding on edits:
   - Run `npm run build:all` unless dependencies are missing.
   - Open or screenshot both `dist/polystore-accountable-retrieval.html` and `dist/polystore-accountable-retrieval-light.html`.
   - Review every slide in both modes when doing a finalization pass, comparing dark and light versions slide-by-slide for parity. For a narrower request, review the target slides plus cover, a normal text slide, an image-heavy slide, and appendix treatment.
   - Use full-size slide screenshots or final PDF rasters for layout judgments. Do not use thumbnail strips/contact sheets as proof of alignment, fit, or hierarchy.
   - Contact sheets are allowed only after full-size review, as a compact summary or navigation aid.
   - Compare repeated deck chrome and footer-zone elements by eye across adjacent screenshots: corner marks, header/eyebrow rails, title anchor points, footer, page number, appendix/section labels, bottom recap/callout strips, and any persistent brand elements.
   - For header claims, measure the rendered rail/title/subhead boxes in the final target artifact when possible. For the current fast-PDF path, rasterize at 96 DPI and compare same-template header boxes against the active template reference.
   - For main-content claims, measure or inspect full-size content bounds: content top, content bottom, card row heights, source-note lane, callout lane, and footer-safe clearance.
   - For full-bleed image, hero, or visual-background slides, verify persistent chrome is still visible above the image/overlay layer. Do not assume section-level background chrome is visible when an absolute visual layer covers the section.
   - Compare the main content bounding box across non-cover slides: top anchor, left/right margins, bottom clearance above the footer zone, and whether slide-specific content starts from the shared template position.
   - Record concrete visual defects before editing: slide order/id, inferred template, mode, affected element, and proposed template-level or content-level fix.
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
   - Content fit: card grids, diagrams, screenshots, source notes, and callouts must fit inside the template content budget without overlap, clipping, or crowding. If the budget fails for several slides, fix the template; if it fails for one slide, tune content only after confirming the template is sound.
   - Components: cards, callouts, metric rows, process steps, diagrams, side panels, source notes.
   - Assets: dark/light pair availability, crop, opacity, contrast, object-fit, visual quality, and whether the image is integral rather than decorative.
   - Marp behavior: global `paginate` and `footer`, cover conventions, and any per-slide `_paginate` exceptions.
   - Narrative order: when slides are reordered, compare the rendered sequence against the intended story arc, not just the source order. Check that moved slides no longer carry stale appendix labels, appendix class names, old speaker-note framing, or page-number exceptions from their previous location.
   - Dead chrome rules: remove unused legacy selectors for old page labels, footer variants, or recap styles once the slide source no longer uses them. Do not leave stale appendix/page-label primitives that could be accidentally reintroduced.

4. Refactor only when duplication is causing visible drift:
   - Add or consolidate shared tokens in `:root`.
   - Create reusable layout primitives for repeated page chrome, reserved footer zones, headers, footers, recap/callout strips, main content frames, cards, panels, figure/image slots, source notes, and two-column/stacked compositions.
   - Prefer named template primitives over slide-specific selectors. A selector may be semantic, but it should bind to template variables rather than defining its own independent frame.
   - When full-bleed templates need persistent chrome, use a shared foreground chrome overlay or shared overlay background tokens rather than per-slide hand-drawn brackets.
   - If content alignment differs across many slides, introduce or strengthen standard templates before tuning individual slides: for example base content frame, title-and-grid, title-and-visual, full-bleed image, appendix, and contact/closing layouts.
   - Replace near-duplicate per-slide rules with component classes when it reduces real drift.
   - Keep slide-specific classes only for semantic layout differences.
   - Prefer shared tokens for margins, corner/chrome offsets, header anchors, title scale, footer/pagination, panel treatment, or figure slots over a broad CSS rewrite.
   - Use export-compatibility shims only when the final artifact demonstrably differs from HTML despite correct template CSS. Name the shim by template behavior, and keep it separate from the `.eyebrow`, card, footer, or chrome primitive.
   - Do not make a broad rename unless it clearly improves maintainability and all references are updated.

5. Polish slides systematically:
   - Normalize title sizing and header rhythm before tuning individual slide internals.
   - Normalize persistent page chrome before slide-specific composition: corner brackets, decorative corner marks, header/eyebrow rails, footer, page number, and appendix label should align to the same tokenized offsets.
   - Check chrome after all full-bleed imagery and overlay masks are applied; if a visual layer covers the section background, restore the chrome in that template's foreground overlay.
   - Establish a reserved bottom safe area before placing diagrams, legends, cards, or callouts. Content may approach the footer zone only through an intentional shared component that accounts for the footer and page number.
   - Normalize non-cover main content to a shared content frame before local layout tweaks. Preserve exceptions only for intentionally full-bleed visual slides, cover/title slides, or slides with a documented alternate template.
   - Resolve content overflow through the template budget first: grid tracks, max heights, source-note lanes, callout lanes, card row sizing, and diagram scale. Only shorten copy or shrink one slide after the template frame is proven correct.
   - Decide the deck-wide recap convention before styling individual takeaways: use concise unlabeled recap phrases, use a named label only when it carries meaning, or remove the recap strip when the footer alone is cleaner.
   - Align recurring elements to shared margins and grid positions.
   - Make every image/diagram feel designed: stable dimensions, intentional crop, consistent border/radius/shadow rules, accessible contrast, and matching dark/light variants.
   - Use existing paired assets first. Use the `imagegen` skill/tool only when a missing or low-quality raster visual is the blocker after auditing existing assets, then wire the result into both themes.
   - Prefer SVG or CSS for crisp diagrams when the deck already uses those patterns; prefer raster images for atmospheric or product-like visual panels.
   - Avoid nested cards, oversized hero type inside compact panels, one-off decorative blobs, and text that can overlap or overflow.

6. Validate both modes:
   - Run `npm run build:all` after edits.
   - For final deck passes, run `npm run pdf`, `npm run pdf:light`, `npm run pptx`, and `npm run pptx:light`. Current PDF scripts render Marp PDFs into temporary files, then run Ghostscript with `-sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH` to create small, fast-loading PDFs with selectable text.
   - Use `soffice` / LibreOffice as the default production PDF generation path when iPhone/mobile compatibility matters. Keep direct Marp and Marp/Ghostscript commands as explicit alternate artifacts for selectable-text or desktop inspection, not as the default deck PDF.
   - Re-open or screenshot the dark and light outputs at full size. For finalization passes, verify every slide in paired dark/light comparison; for narrower changes, verify every touched slide plus representative unaffected slides.
   - Rasterize final PDFs when PDF/PPTX output is part of the change. Measure same-template header rails and inspect full-size content bounds. Do not substitute contact sheets for this step.
   - Check cover, thesis/problem, image-heavy slides, technical diagrams, economics/metrics, status/ask, and appendix.
   - Fix visible drift rather than describing it.

## Design Checklist

Before finishing, confirm:

- Pagination and footer have the same visual system across normal slides, cover, and appendix.
- Dark mode uses pink as primary and cyan as secondary; light mode uses cyan as primary and pink as secondary.
- Eyebrows, normal slide titles, footer rails/text emphasis, page-number dividers, bottom recap/callouts, and principal message elements consume the primary accent through shared tokens.
- Unified card rows use primary-accent card styling unless a secondary/status role is explicitly justified.
- The light-mode cover renders as a light slide with the light logo/visual, not the dark cover.
- Slides reserve the footer/page-number safe area even when a footer element is hidden or intentionally omitted.
- Every non-cover slide has a named template assignment, and any exception template is explicit.
- Decorative page chrome, especially corner brackets and header/eyebrow rails, has consistent offsets, scale, and visibility across same-template slides and modes.
- Header alignment was validated from full-size screenshots or measured final PDF rasters, not thumbnails.
- Full-bleed visual slides do not hide persistent chrome behind image or overlay layers.
- Marp pagination/footer directives still behave intentionally, including any `_paginate` exceptions.
- Main-flow slides use normal page numbers; appendix/section labels only appear where the deck structure actually calls for them.
- Reordered slides have been visually checked against the intended story sequence, and moved main-deck slides do not retain stale appendix/source-position naming or notes.
- No unused legacy appendix/page-label or footer selectors remain after migrating to the shared chrome system.
- Bottom recap/callout strips follow one style and content convention, avoid boilerplate labels repeated slide after slide, and never intrude into the footer/page-number zone.
- Header blocks use consistent title sizes, top/left anchors, subhead spacing, and eyebrow treatment.
- Main content on non-cover slides uses a standard content frame or a named alternate template; cards, legends, diagrams, and captions do not drift into the footer zone.
- Main content was checked at full size for overflow, crowding, clipping, inconsistent card heights, source-note collisions, and callout/footer collisions.
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

Useful final-PDF raster checks:

```bash
rm -rf /tmp/polystore-pdf-pages
mkdir -p /tmp/polystore-pdf-pages
pdftoppm -png -r 96 dist/polystore-accountable-retrieval.pdf /tmp/polystore-pdf-pages/dark
pdftoppm -png -r 96 dist/polystore-accountable-retrieval-light.pdf /tmp/polystore-pdf-pages/light
```

When checking header rail drift, measure full-size rasters for every slide in the same template. The current normal-header PDF reference is `y=81`, `x=77-101` at 96 DPI, but remeasure this when the template changes instead of hard-coding slide numbers.

Use focused commands during iteration, then run the broader set for final delivery.
