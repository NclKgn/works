// astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { readFileSync } from 'fs';
import { parse } from 'yaml';

const visibilityPath = new URL('./src/data/visibility.yaml', import.meta.url);
let hiddenSections = [];
try {
  const raw = readFileSync(visibilityPath, 'utf-8');
  const data = parse(raw);
  hiddenSections = Object.entries(data)
    .filter(([, v]) => !v)
    .map(([k]) => k);
} catch {}

const alwaysHidden = ['/phd/lab', '/phd/meetings', '/admin'];
const hiddenPaths = [
  ...alwaysHidden,
  ...hiddenSections.map((s) => `/${s}`),
];

export default defineConfig({
  site: 'https://nclkgn.github.io',
  base: '/works',
  integrations: [
    sitemap({
      filter: (page) => !hiddenPaths.some((p) => page.includes(p)),
    }),
  ],
  i18n: {
    locales: ['en', 'fr'],
    defaultLocale: 'en',
  },
});
