import { CONTRACT_ADDRESS, STUDIO_NEXT_CHAIN_ID } from './config';
import { WRITE_METHODS } from './workflow';

export type PendingWrite = {
  version: 2;
  chain: number;
  contract: string;
  account: string;
  method: string;
  args: { type: 'string' | 'integer'; value: string }[];
  hash?: `0x${string}`;
  context?: Record<string, string>;
};
const key = `accordlens.pending.v2:${STUDIO_NEXT_CHAIN_ID}:${CONTRACT_ADDRESS?.toLowerCase() ?? 'unconfigured'}`;
let volatile: PendingWrite | undefined;
const methods = Object.keys(WRITE_METHODS);

export function loadPending(): PendingWrite | undefined {
  if (volatile) return volatile;
  const raw = localStorage.getItem(key);
  if (raw === null) return undefined;
  const row = JSON.parse(raw) as PendingWrite;
  if (!row || row.version !== 2 || row.chain !== STUDIO_NEXT_CHAIN_ID || typeof row.contract !== 'string' || row.contract.toLowerCase() !== CONTRACT_ADDRESS?.toLowerCase() || !/^0x[0-9a-fA-F]{40}$/.test(row.account) || !methods.includes(row.method) || !Array.isArray(row.args) || row.args.some(arg => !arg || !['string', 'integer'].includes(arg.type) || typeof arg.value !== 'string' || (arg.type === 'integer' && !/^\d+$/.test(arg.value))) || (row.hash !== undefined && !/^0x[0-9a-fA-F]{64}$/.test(row.hash))) throw new Error('An earlier transaction record needs reconciliation before another write.');
  return row;
}
export function reserveWrite(account: string, method: string, args: unknown[], context?: Record<string, string>): PendingWrite {
  if (loadPending()) throw new Error('An earlier wallet request is still awaiting verification. Do not submit again.');
  if (!CONTRACT_ADDRESS) throw new Error('Contract is not configured.');
  if (!/^0x[0-9a-fA-F]{40}$/.test(account) || !methods.includes(method)) throw new Error('Invalid transaction identity. No write was submitted.');
  const encoded = args.map(value => {
    if (typeof value === 'string') return { type: 'string' as const, value };
    if (typeof value === 'bigint' && value >= 0n && value < 2n ** 256n) return { type: 'integer' as const, value: value.toString() };
    throw new Error('Unsupported transaction argument. No write was submitted.');
  });
  if (context && Object.values(context).some(value => typeof value !== 'string')) throw new Error('Invalid readback context. No write was submitted.');
  const pending: PendingWrite = { version: 2, chain: STUDIO_NEXT_CHAIN_ID, contract: CONTRACT_ADDRESS, account, method, args: encoded, context };
  localStorage.setItem(key, JSON.stringify(pending));
  if (localStorage.getItem(key) !== JSON.stringify(pending)) throw new Error('Transaction recovery storage is unavailable. No write was submitted.');
  volatile = pending;
  return pending;
}
export function recordHash(pending: PendingWrite, hash: `0x${string}`): boolean {
  if (!/^0x[0-9a-fA-F]{64}$/.test(hash)) throw new Error('Invalid transaction hash. Keep the existing request locked.');
  volatile = { ...pending, hash };
  try { localStorage.setItem(key, JSON.stringify(volatile)); return true; } catch { return false; }
}
export function clearVerifiedPending(): void {
  localStorage.removeItem(key);
  if (localStorage.getItem(key) !== null) throw new Error('Recovery cleanup failed. Do not submit again.');
  volatile = undefined;
}
