// src/pages/rss.xml.js
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  const posts = await getCollection('newsletter');
  return rss({
    title: 'Nicolas Kogane — PhD Newsletter',
    description: 'Weekly digests of PhD research on skull base synchondroses.',
    site: context.site,
    items: posts
      .filter((post) => !post.data.draft)
      .sort((a, b) => b.data.date.getTime() - a.data.date.getTime())
      .map((post) => ({
        title: post.data.title,
        pubDate: post.data.date,
        description: post.data.summary,
        link: `${import.meta.env.BASE_URL}phd/newsletter/${post.id}/`,
      })),
  });
}
