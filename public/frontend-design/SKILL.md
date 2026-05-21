# Frontend Design Skill

Modern HTML/CSS patterns for building web UIs.

## What's Covered

- **Layout** — Flexbox for 1D, CSS Grid for 2D layouts
- **Design tokens** — CSS custom properties for colors, spacing, typography
- **Dark mode** — `prefers-color-scheme` + manual toggle via `data-theme`
- **Components** — Button, Card, Badge, Form Input
- **Responsive** — Mobile-first breakpoints (sm/md/lg/xl)
- **Animation** — fade-in, spin, skeleton pulse; respects `prefers-reduced-motion`
- **Accessibility** — `sr-only`, `focus-visible`, ARIA labels, live regions

## Quick Start

```css
:root {
  --color-primary: #3b82f6;
  --font-sans: 'Inter', system-ui, sans-serif;
  --radius-md: 0.375rem;
}

.btn-primary {
  background: var(--color-primary);
  color: #fff;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  border: none;
  cursor: pointer;
}
```

## Responsive Breakpoints

| Name | Min-width |
|------|-----------|
| sm   | 640px     |
| md   | 768px     |
| lg   | 1024px    |
| xl   | 1280px    |

Always write mobile-first: base styles are for small screens, then use `@media (min-width: ...)` to enhance.
