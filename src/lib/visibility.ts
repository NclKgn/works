// src/lib/visibility.ts
import { getCollection } from 'astro:content';

const isDev = import.meta.env.DEV;

export async function isSectionVisible(key: string): Promise<boolean> {
  if (isDev) return true;
  const vis = await getCollection('visibility');
  const entry = vis.find((e) => e.id === key);
  return entry?.data.value ?? false;
}

export async function getVisibleSections(): Promise<string[]> {
  if (isDev) return ['phd', 'projects', 'cv', 'stack', 'labs', 'misc'];
  const vis = await getCollection('visibility');
  return vis.filter((e) => e.data.value).map((e) => e.id);
}
