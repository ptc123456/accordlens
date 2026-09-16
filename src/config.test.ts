import { describe, expect, it } from 'vitest';
import { studioDevnet } from 'genlayer-js/chains';
import { CONTRACT_ADDRESS, STUDIO_NEXT_CHAIN_HEX, STUDIO_NEXT_CHAIN_ID } from './config';
import proxySource from '../api/rpc.ts?raw';
import viteSource from '../vite.config.ts?raw';
import clientSource from './contract.ts?raw';
import vercelSource from '../vercel.json?raw';

describe('preview network binding', () => {
  it('binds UI chain values to the installed preview SDK preset', () => {
    expect(STUDIO_NEXT_CHAIN_ID).toBe(61997);
    expect(studioDevnet.id).toBe(STUDIO_NEXT_CHAIN_ID);
    expect(STUDIO_NEXT_CHAIN_HEX).toBe(`0x${STUDIO_NEXT_CHAIN_ID.toString(16)}`);
  });
  it('does not route the frontend proxy to the historical network', () => {
    for (const source of [proxySource, viteSource]) {
      expect(source).toContain('https://studio-dev.genlayer.com/api');
      expect(source).not.toContain('https://studio.genlayer.com/api');
    }
  });
  it('selects the preview preset for read and wallet clients', () => {
    expect(clientSource.match(/createClient\(\{ chain: studioDevnet/g)).toHaveLength(2);
    expect(clientSource.match(/endpoint: '\/api\/rpc'/g)).toHaveLength(2);
    expect(viteSource).toContain("'/api/rpc'");
  });
  it('binds the verified Studio Dev release contract', () => {
    expect(CONTRACT_ADDRESS).toBe('0xa687ba36bc5457b40e9F3b1Ed6AE167914F6AAF7');
  });
  it('keeps both public SPA routes reloadable without shadowing the RPC function', () => {
    const routes = JSON.parse(vercelSource).rewrites;
    expect(routes).toEqual([
      { source: '/council', destination: '/index.html' },
      { source: '/how-it-works', destination: '/index.html' },
    ]);
    expect(routes.some(({ source }: { source: string }) => source.startsWith('/api'))).toBe(false);
  });
});
