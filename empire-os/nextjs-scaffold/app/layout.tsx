import './globals.css';
import type { Metadata } from 'next';
import Link from 'next/link';
import React from 'react';

export const metadata: Metadata = {
  title: 'DreamCo Empire OS',
  description: 'Next.js 14 marketplace shell for DreamCo Empire OS.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100">
        <header className="border-b border-slate-800 bg-slate-900/80">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
            <div>
              <h1 className="text-xl font-semibold">DreamCo Empire OS</h1>
              <p className="text-sm text-slate-400">Autonomous revenue fleet management</p>
            </div>
            <nav className="flex gap-4 text-sm text-slate-300">
              <Link href="/">Marketplace</Link>
              <Link href="/bots/dreambot">DreamBot</Link>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-6 py-10">{children}</main>
        <footer className="border-t border-slate-800 px-6 py-6 text-sm text-slate-500">
          <div className="mx-auto max-w-6xl">DreamCo Empire OS • Next.js 14 App Router scaffold</div>
        </footer>
      </body>
    </html>
  );
}
