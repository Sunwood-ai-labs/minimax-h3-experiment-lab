import { defineConfig } from 'vitepress'

const base = process.env.DOCS_BASE ?? '/'

const englishNav = [
  { text: 'Guide', link: '/guide/reproduce' },
  { text: 'Experiments', link: '/guide/experiments' },
  { text: 'Repository', link: 'https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab' },
  { text: '日本語', link: '/ja/' },
]

const japaneseNav = [
  { text: 'ガイド', link: '/ja/guide/reproduce' },
  { text: '実験一覧', link: '/ja/guide/experiments' },
  { text: 'Repository', link: 'https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab' },
  { text: 'English', link: '/' },
]

const englishSidebar = [
  {
    text: 'Getting started',
    items: [
      { text: 'Reproduce an experiment', link: '/guide/reproduce' },
      { text: 'Experiment structure', link: '/guide/records' },
      { text: 'Experiment index', link: '/guide/experiments' },
    ],
  },
]

const japaneseSidebar = [
  {
    text: 'はじめに',
    items: [
      { text: '実験を再現する', link: '/ja/guide/reproduce' },
      { text: '実験の構成', link: '/ja/guide/records' },
      { text: '実験一覧', link: '/ja/guide/experiments' },
    ],
  },
]

export default defineConfig({
  base,
  title: 'MiniMax-H3 Experiment Lab',
  description: 'Reproducible Docker Compose and ComfyUI experiments for MiniMax-H3 video generation.',
  cleanUrls: true,
  lastUpdated: true,
  head: [['link', { rel: 'icon', href: `${base}icon.svg` }]],
  locales: {
    root: { label: 'English', lang: 'en' },
    ja: { label: '日本語', lang: 'ja', link: '/ja/' },
  },
  themeConfig: {
    logo: { src: '/icon.svg', alt: 'MiniMax-H3 Experiment Lab' },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab' },
    ],
    search: { provider: 'local' },
    locales: {
      root: { label: 'English', nav: englishNav, sidebar: englishSidebar },
      ja: { label: '日本語', nav: japaneseNav, sidebar: japaneseSidebar },
    },
  },
})
