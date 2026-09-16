import { beforeEach, describe, expect, it, vi } from 'vitest';
vi.mock('./config', () => ({ CONTRACT_ADDRESS: `0x${'2'.repeat(40)}`, STUDIO_NEXT_CHAIN_ID: 61997 }));
let data: Map<string, string>;
const account = `0x${'1'.repeat(40)}`;
const hash = `0x${'3'.repeat(64)}` as const;
beforeEach(() => {
  vi.resetModules();
  data = new Map();
  vi.stubGlobal('localStorage', { getItem: (key: string) => data.get(key) ?? null, setItem: (key: string, value: string) => data.set(key, value), removeItem: (key: string) => data.delete(key) });
});
describe('chain-bound recovery journal', () => {
  it('restores exact pending identity after a module reload', async () => {
    const first = await import('./recovery');
    const pending = first.reserveWrite(account, 'activate_change', [7n]);
    first.recordHash(pending, hash);
    vi.resetModules();
    const fresh = await import('./recovery');
    expect(fresh.loadPending()).toMatchObject({ chain: 61997, account, method: 'activate_change', hash, args: [{ type: 'integer', value: '7' }] });
    expect(() => fresh.reserveWrite(account, 'activate_change', [7n])).toThrow('Do not submit again');
  });
  it('keeps the returned hash in memory if post-hash storage fails', async () => {
    const journal = await import('./recovery');
    const pending = journal.reserveWrite(account, 'activate_change', [7n]);
    vi.stubGlobal('localStorage', { getItem: (key: string) => data.get(key) ?? null, setItem: () => { throw new Error('quota'); } });
    expect(journal.recordHash(pending, hash)).toBe(false);
    expect(journal.loadPending()?.hash).toBe(hash);
  });
  it('fails closed on malformed or wrong-chain persisted records without deleting them', async () => {
    const journal = await import('./recovery');
    journal.reserveWrite(account, 'activate_change', [7n]);
    const key = [...data.keys()][0];
    const saved = JSON.parse(data.get(key)!);
    data.set(key, JSON.stringify({ ...saved, chain: 61999 }));
    vi.resetModules();
    const fresh = await import('./recovery');
    expect(() => fresh.loadPending()).toThrow('reconciliation');
    expect(data.has(key)).toBe(true);
  });
});
