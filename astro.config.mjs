// astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://nclkgn.github.io',
  base: '/works',
  integrations: [
    sitemap({
      filter: (page) =>
        !page.includes('/phd/lab') &&
        !page.includes('/phd/meetings') &&
        !page.includes('/admin'),
    }),
  ],
  i18n: {
    locales: ['en', 'fr'],
    defaultLocale: 'en',
  },
});
