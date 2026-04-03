// src/content.config.ts
import { defineCollection } from 'astro:content';
import { glob, file } from 'astro/loaders';
import { z } from 'astro/zod';

// ── Markdown collections (glob) ──

const newsletter = defineCollection({
  loader: glob({ base: './src/content/newsletter', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    summary: z.string(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

const projects = defineCollection({
  loader: glob({ base: './src/content/projects', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    status: z.enum(['ongoing', 'completed', 'upcoming']),
    domain: z.array(z.enum(['research', 'clinical', 'engineering'])),
    summary: z.string(),
    collaborators: z.array(z.string()).default([]),
    order: z.number().default(0),
    draft: z.boolean().default(false),
  }),
});

const misc = defineCollection({
  loader: glob({ base: './src/content/misc', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    category: z.string(),
    date: z.coerce.date().optional(),
    draft: z.boolean().default(false),
  }),
});

// ── YAML data collections (file) ──

const cv = defineCollection({
  loader: file('./src/data/cv.yaml'),
  schema: z.object({
    section: z.enum(['education', 'clinical', 'research', 'skills']),
    year: z.string(),
    title: z.string(),
    institution: z.string(),
    description: z.string(),
  }),
});

const stack = defineCollection({
  loader: file('./src/data/stack.yaml'),
  schema: z.object({
    layer: z.string(),
    methods: z.string(),
    tools: z.string(),
    description: z.string(),
    order: z.number(),
  }),
});

const labs = defineCollection({
  loader: file('./src/data/labs.yaml'),
  schema: z.object({
    name: z.string(),
    pi: z.string(),
    institution: z.string(),
    role: z.string(),
    work: z.string(),
    url: z.string().optional(),
  }),
});

const phdProgress = defineCollection({
  loader: file('./src/data/phd-progress.yaml'),
  schema: z.object({
    label: z.string(),
    value: z.number(),
    color: z.string().optional(),
  }),
});

const hero = defineCollection({
  loader: file('./src/data/hero.yaml'),
  schema: z.object({
    name: z.string(),
    tagline: z.string(),
    description: z.string(),
  }),
});

const visibility = defineCollection({
  loader: file('./src/data/visibility.yaml'),
  schema: z.boolean(),
});

// ── Private collections (lab notebook, meetings) ──

const labEntries = defineCollection({
  loader: glob({ base: './src/content/lab-entries', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

const meetings = defineCollection({
  loader: glob({ base: './src/content/meetings', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    attendees: z.array(z.string()).default([]),
    decisions: z.array(z.string()).default([]),
    actions: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

export const collections = {
  newsletter,
  projects,
  misc,
  cv,
  stack,
  labs,
  hero,
  'phd-progress': phdProgress,
  'lab-entries': labEntries,
  meetings,
  visibility,
};
