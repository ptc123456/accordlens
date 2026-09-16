import type { AnnouncedProvider } from './wallet';
import { isSuccessful } from 'genlayer-js';
import { providerClient, finalizedTransaction } from './contract';
import { CONTRACT_ADDRESS, CONTRACT_ADDRESS_VALID, STUDIO_NEXT_CHAIN_HEX } from './config';
import { loadPending, reserveWrite, recordHash, clearVerifiedPending } from './recovery';

export type TransactionStage = 'IDLE' | 'WAITING_FOR_WALLET' | 'SUBMITTED' | 'WAITING_FOR_FINALITY' | 'VERIFYING_EXECUTION' | 'VERIFYING_READBACK' | 'SUCCESS' | 'REJECTED' | 'FAILED' | 'RECONCILIATION_REQUIRED';
export type TransactionState = { hash: `0x${string}`; stage: TransactionStage; message: string };
const JOURNAL_KEY = 'accordlens.transaction-journal.v1';
export function readJournal(): `0x${string}`[] { try { const value = JSON.parse(localStorage.getItem(JOURNAL_KEY) ?? '[]'); return Array.isArray(value) ? value.filter(x => typeof x === 'string' && /^0x[0-9a-fA-F]+$/.test(x)) : []; } catch { return []; } }
export function retainHash(hash: string): void { if (!/^0x[0-9a-fA-F]+$/.test(hash)) return; const next = Array.from(new Set([...readJournal(), hash])); localStorage.setItem(JOURNAL_KEY, JSON.stringify(next.slice(-8))); }
export function classifyTransaction(value: unknown): { finalized: boolean; success: boolean; message: string } {
  const row = (value && typeof value === 'object' ? value : {}) as Record<string, unknown>;
  const finalized = row.lifecycle === 'finalized' || row.statusName === 'FINALIZED';
  const success = finalized && isSuccessful(row as Parameters<typeof isSuccessful>[0]);
  return { finalized, success, message: finalized && success ? 'Finalized execution verified. Contract readback is still required.' : finalized ? 'Finalized, but successful semantic execution is not verified.' : 'Waiting for finality.' };
}
let submitting = false;
export async function submitWrite(item: AnnouncedProvider, account: `0x${string}`, functionName: string, args: unknown[], onState: (state: TransactionState) => void, context?: Record<string, string>): Promise<`0x${string}`> {
  if (submitting || loadPending()) throw new Error('An earlier wallet request needs verification. Do not submit again.');
  submitting = true;
  try { return await submitUnlocked(item, account, functionName, args, onState, context); }
  catch (cause) { const code = (cause as { code?: number; cause?: { code?: number } })?.code ?? (cause as { cause?: { code?: number } })?.cause?.code; if (code !== 4001 && !loadPending()) onState({ hash: '0x', stage: 'FAILED', message: cause instanceof Error ? cause.message : 'The transaction could not be submitted.' }); throw cause; }
  finally { submitting = false; }
}
async function submitUnlocked(item: AnnouncedProvider, account: `0x${string}`, functionName: string, args: unknown[], onState: (state: TransactionState) => void, context?: Record<string, string>): Promise<`0x${string}`> {
  if (!CONTRACT_ADDRESS_VALID || !CONTRACT_ADDRESS) throw new Error('The accepted contract address is not configured.');
  onState({ hash: '0x', stage: 'WAITING_FOR_WALLET', message: 'Confirm this action in your wallet.' });
  const client = providerClient(item, account);
  const call = { address: CONTRACT_ADDRESS as `0x${string}`, functionName, args: args as never[], value: 0n };
  const estimate = await client.estimateTransactionFeesForWrite(call);
  const chain = await item.provider.request({ method: 'eth_chainId' });
  if (String(chain).toLowerCase() !== STUDIO_NEXT_CHAIN_HEX) throw new Error('Switch this wallet to GenLayer Studio Dev before submitting.');
  const accounts = await item.provider.request({ method: 'eth_accounts' });
  if (!Array.isArray(accounts) || typeof accounts[0] !== 'string' || accounts[0].toLowerCase() !== account.toLowerCase()) throw new Error('The selected wallet account changed. Reconnect before submitting.');
  const balance = await item.provider.request({ method: 'eth_getBalance', params: [account, 'latest'] });
  if (typeof balance !== 'string' || !/^0x[0-9a-fA-F]+$/.test(balance)) throw new Error('The selected wallet balance could not be verified.');
  if (BigInt(balance) < estimate.feeValue) throw new Error('The selected account has insufficient GEN for the estimated protocol fee. Fund this account before trying again.');
  const pending = reserveWrite(account, functionName, args, context);
  let rawHash: unknown;
  try { rawHash = await client.writeContract({ ...call, fees: { distribution: estimate.distribution, messageAllocations: estimate.messageAllocations, feeValue: estimate.feeValue } }); }
  catch (cause) {
    const error = cause as { code?: number; cause?: { code?: number } };
    if (error?.code === 4001 || error?.cause?.code === 4001) { clearVerifiedPending(); onState({ hash: '0x', stage: 'REJECTED', message: 'The wallet request was rejected. No transaction was submitted.' }); }
    else onState({ hash: '0x', stage: 'RECONCILIATION_REQUIRED', message: 'The wallet response is uncertain. Check the existing request before trying again.' });
    throw cause;
  }
  if (typeof rawHash !== 'string' || !/^0x[0-9a-fA-F]{64}$/.test(rawHash)) { onState({ hash: '0x', stage: 'RECONCILIATION_REQUIRED', message: 'The wallet returned no transaction hash. Check wallet activity before trying again.' }); throw new Error('Wallet returned no valid transaction hash. Reconcile the wallet request before submitting again.'); }
  const hash = rawHash as `0x${string}`;
  const persisted = recordHash(pending, hash);
  onState({ hash, stage: 'SUBMITTED', message: persisted ? 'Transaction submitted.' : 'Submitted, but recovery storage failed. Keep this page and transaction hash.' });
  onState({ hash, stage: 'WAITING_FOR_FINALITY', message: 'Waiting for GenLayer finality and consensus.' }); return hash;
}
export async function waitForFinality(item: AnnouncedProvider, hash: `0x${string}`, onState: (state: TransactionState) => void, maxPolls = 30): Promise<unknown> {
  try {
    const result = await finalizedTransaction(hash, maxPolls);
    const status = classifyTransaction(result);
    if (!status.finalized || !status.success) throw new Error(status.message);
    onState({ hash, stage: 'VERIFYING_EXECUTION', message: status.message });
    return result;
  } catch (cause) {
    onState({ hash, stage: 'RECONCILIATION_REQUIRED', message: 'Verification was interrupted. Continue checking this transaction; do not submit it again.' });
    throw cause;
  }
}
