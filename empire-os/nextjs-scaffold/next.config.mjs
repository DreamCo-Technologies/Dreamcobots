import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.cwd(), '..', '..');
const botsDir = path.join(root, 'bots');

function readBotSlugs() {
  if (!fs.existsSync(botsDir)) return [];
  return fs
    .readdirSync(botsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((slug) => fs.existsSync(path.join(botsDir, slug, 'bot_profile.json')));
}

const nextConfig = {
  reactStrictMode: true,
  experimental: {
    typedRoutes: true,
  },
  env: {
    DREAMCO_BOT_COUNT: String(readBotSlugs().length),
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-DreamCo-Platform', value: 'Empire-OS' },
          { key: 'X-DreamCo-Bot-Count', value: String(readBotSlugs().length) },
        ],
      },
    ];
  },
};

export default nextConfig;
