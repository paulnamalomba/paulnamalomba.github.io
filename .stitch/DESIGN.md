# Paul Namalomba Portfolio Design System

## Product intent

A professional portfolio and technical knowledge base for a computational engineer who works across scientific software, backend systems, data platforms and infrastructure. The experience should communicate technical depth without reading like a long CV or a wall of technology badges.

The main portfolio and Tech Guides are in scope. Interview preparation, assessments, learning notes and conference presentations remain independent routes and must not be redesigned or surfaced in primary navigation.

## Design character

- Editorial engineering: rigorous, calm, clear and slightly tactile.
- Confident typography and generous negative space instead of decorative effects.
- Project evidence before exhaustive skills.
- A publication-like Tech Guides experience, distinct from a generic documentation directory.
- Inspired by strong contemporary portfolio information architecture, without copying the Nuxt portfolio template.

## Color tokens

- Paper: `#F2F0E9`
- Deep paper: `#E7E3D9`
- Ink: `#121715`
- Soft ink: `#38413D`
- Rule: `#C9C7BE`
- Primary teal: `#07857D`
- Deep teal: `#075D59`
- Project blue: `#3157D5`
- Signal acid: `#D8FF62`
- Warm white: `#FFFEF8`

Use teal for identity and editorial emphasis, blue for selected product work, and acid only for high-value calls to action or featured knowledge. Avoid gradients, glassmorphism and excessive shadows.

## Typography

- Primary sans: Inter or a high-quality system grotesk (`Segoe UI`, Helvetica, Arial).
- Editorial accent: Georgia italic, used sparingly inside large display headlines.
- Display headings: bold, compact line height, negative tracking.
- Eyebrows and metadata: uppercase, small, strongly tracked.
- Code and numeric indices: system monospace.

## Shape and spacing

- Most layout surfaces use square corners and thin rules.
- Project feature cards may use a restrained `20px` radius.
- Buttons are rectangular, compact and content-led.
- Desktop content width: approximately `1180px`.
- Section spacing: `80px` to `144px` desktop, `64px` to `88px` mobile.
- All interactive targets must remain at least `44px` on touch layouts.

## Main portfolio structure

1. Sticky brand navigation: Work, Tech Guides, Experience, About, Contact.
2. Hero: positioning statement, short supporting copy, portrait, CV action and four proof metrics.
3. Selected work: SESKA, Ecoride and SEAT as the primary case studies; HalfQR, DataShadric, Smart Lame and ComputeMore as concise supporting work.
4. Tech Guides: three featured field notes and a strong route to the complete knowledge base.
5. Experience: compact timeline focused on responsibility and outcomes.
6. Capabilities: computational engineering, backend systems, data platforms and delivery/infrastructure.
7. About and education.
8. Direct contact call to action. Do not publish referee contact details.

## Tech Guides structure

- Knowledge-base home with two clear paths: Technical Guides and System Scripts.
- All Guides page with search, category filters, three featured guides and a responsive guide grid.
- Categories: Backend & Architecture, Data & Performance, Infrastructure & Tooling, Systems Engineering.
- Article pages use a readable centered column, persistent portfolio navigation, breadcrumbs, strong heading hierarchy, accessible tables and horizontally scrollable code blocks.

## Responsive behavior

- Desktop project layouts collapse to one column below tablet width.
- Primary navigation becomes a full-screen mobile overlay with an explicit close state.
- Metrics use a two-column mobile grid.
- Guide filters wrap rather than overflow.
- Large headlines must use fluid sizing and never create horizontal scrolling.
- Respect `prefers-reduced-motion`.

## Accessibility

- Semantic landmarks and one primary `h1` per page.
- Visible keyboard focus and a working skip link.
- Real text labels for all icon-only controls.
- Meaningful image alternative text; decorative imagery should be hidden from assistive technology.
- Minimum AA contrast for body text and controls.
