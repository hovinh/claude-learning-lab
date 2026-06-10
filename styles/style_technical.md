# Midnight Executive — Presentation Style Template

Use this file as a reference when asking Claude to build a new `.pptx` in this style.
Paste the relevant sections into your prompt, or hand Claude the whole file.

---

## 1. Identity

| Property | Value |
|---|---|
| Theme name | Midnight Executive |
| Slide size | 13.3" × 7.5" (LAYOUT_WIDE, 16:9) |
| Library | pptxgenjs (Node.js) |

---

## 2. Colour Palette

```js
const C = {
  navy:    "1E2761",   // primary — backgrounds, headers, accents
  ice:     "CADCFC",   // secondary — subtitles, highlights on dark
  white:   "FFFFFF",
  bg:      "F4F7FF",   // light slide background
  muted:   "8899BB",   // captions, footnotes, slide numbers
  dark:    "2D3B6E",   // body text on light slides
  card:    "3D4F7C",   // body text inside cards
  code_bg: "1A1F3A",   // dark terminal background
  green:   "4ECDC4",   // $ prompt in code blocks
};
```

---

## 3. Typography

| Role | Font | Size | Style |
|---|---|---|---|
| Slide title (content) | Georgia | 26 pt | Bold, white |
| Main title (title slide) | Georgia | 48 pt | Bold, white |
| Section number | Georgia | 96 pt | Bold, ice, ~25% transparent |
| Section title | Georgia | 40 pt | Bold, white |
| Card heading | Georgia | 13–16 pt | Bold, dark |
| Body / bullets | Calibri | 12–14 pt | Regular, card |
| Code | Consolas | 11.5 pt | Regular |
| Captions / footnotes | Calibri | 10–11 pt | Italic, muted |
| Slide number | Calibri | 10 pt | Regular, muted, bottom-right |

---

## 4. Slide Types

### 4.1 Title Slide
- Full navy background
- Large faint circle top-right: ice blue, ~88% transparent
- Ice blue vertical bar (0.08" wide) left of content
- Docker/topic icon above title
- Georgia 48pt bold white title
- Ice blue subtitle, muted italic audience line
- Italic muted source credit bottom-left

### 4.2 Section Divider
- Full navy background
- Large faint circle top-right
- 96pt Georgia section number, ice, 25% transparent
- Horizontal rule (ice, 50% transparent) across slide
- 40pt Georgia bold white section title
- 17pt Calibri italic ice subtitle tagline

### 4.3 Content Slide (standard)
- Light bg (`F4F7FF`)
- Full-width navy header bar (h = 1.05"), 26pt Georgia bold white title
- Content starts at y = 1.3"
- Slide number bottom-right

### 4.4 Two-Column Layout
- Left: bullet text or code block (w ≈ 5.8–6.1")
- Right: white card with accent stripe (w ≈ 5.4–5.7")

### 4.5 Three-Column Card Grid
- Three equal white cards, navy top stripe
- Icon top-left of card, Georgia bold title, Calibri bullets (`valign: "top"`)

### 4.6 Code Block
- Dark panel (`1A1F3A`) with ice border (60% transparent)
- Three macOS dots (red `E06C75`, yellow `E5C07B`, green `98C379`) top-left
- `$` prompt: green (`4ECDC4`), bold
- `#` comments: muted, italic
- All other lines: `E5E5E5`
- Font: Consolas 11.5pt

### 4.7 Concept / Architecture Map
- White cards with navy top stripe, dashed muted connector lines
- Docker Engine node in full navy (prominent centre)
- Tiered rows: Registry → Engine → Core objects → Orchestration
- Tinted callout bar at bottom for audience-specific note

### 4.8 Glossary Grid
- 2 × N white cards
- Navy monospace badge for the term (Consolas, ice text)
- Calibri body definition below

---

## 5. Decorative Motif

Scattered dot cluster, top-right corner of every slide:

```js
const dots = [
  { x: 12.55, y: 0.28, r: 0.18, op: 22 },  // dark slides
  { x: 12.95, y: 0.75, r: 0.13, op: 18 },
  { x: 12.2,  y: 0.65, r: 0.10, op: 15 },
  { x: 12.75, y: 1.2,  r: 0.08, op: 13 },
  { x: 12.4,  y: 1.45, r: 0.06, op: 10 },
  { x: 13.05, y: 1.5,  r: 0.05, op:  9 },
];
// Light slides: halve the opacity values above
// Color: ice (CADCFC) on dark slides, navy (1E2761) on light slides
```

No connecting lines — circles only.

---

## 6. White Card Component

```js
function addCard(slide, x, y, w, h, accent = "CADCFC") {
  slide.addShape("rect", {
    x, y, w, h,
    fill: { color: "FFFFFF" },
    line: { color: "E0E8F8", width: 0.75 },
    shadow: { type: "outer", blur: 6, offset: 2, angle: 135,
              color: "000000", opacity: 0.10 }
  });
  // Thin accent stripe along top
  slide.addShape("rect", {
    x, y, w, h: 0.07,
    fill: { color: accent }, line: { color: accent, width: 0 }
  });
}
```

---

## 7. Layout Measurements

| Element | x | y | w | h |
|---|---|---|---|---|
| Header bar | 0 | 0 | 13.3" | 1.05" |
| Content start (y) | — | 1.3" | — | — |
| Left margin | 0.55" | — | — | — |
| Right margin | 0.5" | — | — | — |
| Slide number | W−0.5" | H−0.35" | 0.4" | 0.25" |
| Card internal padding | 0.12–0.15" | | | |
| Gap between elements | 0.3–0.5" | | | |

---

## 8. Slide Structure Convention

```
Slide 1        — Title
Slide 2        — Section divider 01
Slides 3–N     — Content slides for section 01
Slide N+1      — Section divider 02
...
Second-to-last — Cheat sheet / reference
Last           — Closing (navy, centred, icon + tagline)
```

---

## 9. Prompt Template

When asking Claude to build a new deck in this style, use:

```
Build a pptx presentation on [TOPIC] using the Midnight Executive style
defined in midnight_executive_template.md.

Audience: [e.g. data scientists / backend engineers / product managers]
Source material: [book / paper / course title]
Sections:
  01. [Section title] — [one-line description]
  02. [Section title] — [one-line description]
  ...

Include:
  - Title slide and closing slide
  - Section dividers for each section
  - Code blocks wherever commands or syntax are demonstrated
  - Glossary slide for technical terms
  - Concept map slide tying the ecosystem together

Output: /mnt/user-data/outputs/[topic]_deck.pptx
```

---

## 10. Icon Usage

Use `react-icons/fa` and `react-icons/md` rendered to PNG via `sharp`.
Render each icon twice: once in ice (`CADCFC`) for dark slides,
once in navy (`1E2761`) for light slides.

```js
async function icon(Comp, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(Comp, { color: `#${color}`, size: String(size) })
  );
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}
```