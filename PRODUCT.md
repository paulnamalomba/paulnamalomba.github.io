# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

The primary audience is prospective clients and engineering collaborators. They
need to understand Paul Namalomba's expertise, examine relevant work, and decide
whether to start a conversation about an engineering problem or collaboration.

## Product purpose

This is Paul Namalomba's personal portfolio and technical resource library. It
demonstrates computational engineering, scientific software, backend/API
development, and data engineering through real projects and practical writing.

Success means visitors can assess the relevance of Paul's work, find supporting
technical evidence, and make a useful collaboration or consultancy inquiry.
Reading resources and downloading the CV also support that assessment.

## Positioning

The portfolio connects computational mechanics and scientific computing with
production software and data systems. Its evidence spans research software,
mobility platforms, and institutional enrolment systems rather than presenting
these disciplines as unrelated skills.

## Operating context

- Visitors explore selected work, experience, capabilities, and professional
  background from `index.html`.
- They can follow project links, visit GitHub and LinkedIn, download
  `Paul-Namalomba_Curriculum-Vitae.pdf`, or contact Paul through an email link.
- `docs/` provides a technical knowledge base. `docs/guides/` supports text search
  and category filtering; `docs/system-scripts/` contains script reference pages.
- Existing supporting sections include the IBM data engineering learning hub at
  `learning/ibm-data-engineering/`, interview preparation at
  `interviews/uct-cto/`, and research slides at `presentations/africomp7/`.

## Capabilities and constraints

- The confirmed platform is a static HTML/CSS/JavaScript website hosted on GitHub
  Pages. Preserve compatibility with static hosting and existing public routes.
- The existing project has no frontend framework or bundler. `package.json`
  provides Prettier formatting; it does not define a development server or build
  command. A local static HTTP server can serve the site for inspection.
- The portfolio supports mobile navigation and links to real project screenshots,
  technical articles, a CV, and professional profiles. Contact currently uses
  `mailto:` rather than an implemented form service.
- Documentation and learning pages have generation code in
  `scripts/build-docs.py` and `scripts/build-learning.py`. Future changes to
  generated pages must account for regeneration and their source material.
- `.github/workflows/deploy-docs.yml` includes a manually triggered Pages workflow
  that imports guides and scripts from `paulnamalomba/system-management_scripts`.
  Preserve this source relationship when changing documentation workflows.
- The user confirmed the product summary and stated no additional requirements
  during initialization on 2026-10-13. No specific accessibility standard was set.

### Open factual decisions

- The canonical contact email is unconfirmed: `index.html` uses
  `paulkbnamalomba@gmail.com`, while `README.md` uses
  `kabwenzenamalomba@gmail.com`. Resolve this before changing contact details.
- The latest SEAT contract start date differs between sources: `index.html`
  says December 2025; `README.md` says November 2025. Confirm before changing
  professional history. Current employment and education status also require
  confirmation when updated.

## Brand commitments

Preserve the identity and name Paul Namalomba, the names of real projects, and
the accuracy of professional and technical content. Existing portfolio copy uses
first-person descriptions and concrete engineering terminology. Initialization
does not establish a new visual direction.

## Evidence on hand

- `index.html` and `README.md` contain project descriptions, professional
  experience, capabilities, and resource links. They are published source
  material, with the factual conflicts noted above still unresolved.
- The three featured projects are Ecoride, SESKA, and SEAT. Existing screenshots
  are in `assets/ecoride_*`, `assets/seska_*`, and `assets/seat_*`.
- Portrait assets include `assets/paul.jpg`, `assets/paul-header.png`, and
  `assets/paul-portrait.png`.
- `Paul-Namalomba_Curriculum-Vitae.pdf` is the existing downloadable CV.
- Technical Markdown and HTML are in `docs/guides/`; learning source notes are
  in `learning/ibm-data-engineering/raw-markdown/`.
- Existing research presentation content and assets are in
  `presentations/africomp7/`.

Existing claims and metrics are source content, not independently verified
evidence. Do not invent client endorsements, outcomes, certifications, or
performance figures to strengthen the portfolio.

## Product principles

1. Help prospective collaborators assess fit through relevant work and evidence.
2. Connect scientific computing, backend systems, and data engineering through
   concrete problems and contributions.
3. Keep technical resources useful for understanding and applying the work.
4. Preserve factual accuracy and resolve conflicting sources before changing
   professional claims.
5. Keep projects, resources, the CV, and contact paths usable on static hosting.
