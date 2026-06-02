import fs from 'node:fs';
import path from 'node:path';
import { notFound } from 'next/navigation';

const root = path.resolve(process.cwd(), '..', '..', '..');
const botsDir = path.join(root, 'bots');

function readProfile(slug: string) {
  const profilePath = path.join(botsDir, slug, 'replit_profile.json');
  if (!fs.existsSync(profilePath)) return null;
  return JSON.parse(fs.readFileSync(profilePath, 'utf8')) as Record<string, any>;
}

export async function getStaticPaths() {
  return fs
    .readdirSync(botsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => ({ params: { slug: entry.name } }));
}

export async function generateStaticParams() {
  const items = await getStaticPaths();
  return items.map((item) => item.params);
}

export default function BotPage({ params }: { params: { slug: string } }) {
  const profile = readProfile(params.slug);
  if (!profile) notFound();
  return (
    <section className="space-y-6">
      <div>
        <p className="text-sm uppercase tracking-wide text-cyan-400">{profile.division}</p>
        <h2 className="text-4xl font-semibold">{profile.displayName ?? params.slug}</h2>
        <p className="mt-3 max-w-3xl text-slate-300">{profile.description}</p>
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-xl border border-slate-800 p-6">
          <h3 className="text-lg font-medium">Capabilities</h3>
          <ul className="mt-4 space-y-2 text-slate-300">
            {(profile.capabilities ?? []).map((capability: string) => (
              <li key={capability}>• {capability}</li>
            ))}
          </ul>
        </div>
        <div className="rounded-xl border border-slate-800 p-6">
          <h3 className="text-lg font-medium">Commercial Profile</h3>
          <p className="mt-4 text-slate-300">Tier: {profile.tier}</p>
          <p className="text-slate-300">Revenue model: {profile.revenueModel}</p>
          <p className="text-slate-300">Pricing: {profile.priceRange}</p>
          <p className="text-slate-300">Target users: {profile.targetUsers}</p>
        </div>
      </div>
    </section>
  );
}
