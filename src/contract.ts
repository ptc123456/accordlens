import { createClient } from 'genlayer-js';
import { studioDevnet } from 'genlayer-js/chains';
import { CONTRACT_ADDRESS, STUDIO_NEXT_CHAIN_HEX } from './config';
import type { AnnouncedProvider } from './wallet';

type Client = ReturnType<typeof createClient>;
type JsonValue = boolean | string | number | null | JsonValue[] | { [key: string]: JsonValue };
const readClient = createClient({ chain: studioDevnet, endpoint: '/api/rpc' });
const inFlight = new Map<string, Promise<JsonValue>>();

function address(): `0x${string}` { if (!CONTRACT_ADDRESS || !/^0x[0-9a-fA-F]{40}$/.test(CONTRACT_ADDRESS)) throw new Error('The accepted contract address is not configured.'); return CONTRACT_ADDRESS as `0x${string}`; }
function decode(value: unknown): JsonValue { if (typeof value === 'string') { try { return JSON.parse(value) as JsonValue; } catch { throw new Error('Contract returned invalid JSON.'); } } if (value === null || typeof value === 'boolean' || typeof value === 'number' || Array.isArray(value) || typeof value === 'object') return value as JsonValue; throw new Error('Contract returned an invalid value.'); }
export async function readView(functionName: string, args: (string | bigint)[] = [], client: Client = readClient): Promise<JsonValue> {
  const contract = address();
  const key = `${STUDIO_NEXT_CHAIN_HEX}:${contract.toLowerCase()}:${functionName}:${args.map(value => typeof value === 'bigint' ? `n:${value}` : `s:${value.length}:${value}`).join('|')}`;
  if (client !== readClient) return decode(await client.readContract({ address: contract, functionName, args }));
  const existing = inFlight.get(key);
  if (existing) return existing;
  const pending = client.readContract({ address: contract, functionName, args }).then(decode);
  inFlight.set(key, pending);
  try { return await pending; } finally { if (inFlight.get(key) === pending) inFlight.delete(key); }
}
export async function readCounts(client: Client = readClient): Promise<JsonValue> { return readView('get_counts', [], client); }
export async function readChange(id: number, client: Client = readClient): Promise<JsonValue> { if (!Number.isSafeInteger(id) || id < 0) throw new Error('Proposal id must be a non-negative integer.'); return readView('get_change', [BigInt(id)], client); }
export function providerClient(detail: AnnouncedProvider, account?: `0x${string}`): Client { return createClient({ chain: studioDevnet, endpoint: '/api/rpc', provider: detail.provider as never, account }); }
export function expectedChain(): string { return STUDIO_NEXT_CHAIN_HEX; }
export function finalizedTransaction(hash: `0x${string}`, retries = 30) {
  if (!/^0x[0-9a-fA-F]{64}$/.test(hash)) throw new Error('Invalid transaction hash.');
  return readClient.waitForFinalization({ hash: hash as never, interval: 20000, retries, fullTransaction: true });
}
