import { finalizedTransaction, readView } from './contract';
import { classifyTransaction } from './transaction';
import { clearVerifiedPending, loadPending } from './recovery';
import { verifyCreate, verifyTransition, type ProposalSnapshot } from './readback';
import type { WriteMethod } from './workflow';
import type { TransactionState } from './transaction';
let active = false;

export async function reconcilePendingWrite(onState?: (value: TransactionState) => void) {
  if (active) throw new Error('Transaction verification is already running.');
  const pending = loadPending();
  if (!pending?.hash || !pending.context) throw new Error('The saved request lacks a hash or readback context. Keep it locked for reconciliation.');
  active = true;
  let terminalFailure = false;
  try {
    onState?.({ hash: pending.hash, stage: 'WAITING_FOR_FINALITY', message: 'Waiting for GenLayer finality and consensus.' });
    const receipt = await finalizedTransaction(pending.hash);
    const outcome = classifyTransaction(receipt);
    if (!outcome.finalized || !outcome.success) { terminalFailure = outcome.finalized; throw new Error(outcome.message); }
    onState?.({ hash: pending.hash, stage: 'VERIFYING_EXECUTION', message: 'Finalized. Verifying execution and consensus.' });
    const consensus = receipt.resultName ?? (receipt as unknown as Record<string, unknown>).result_name;
    if (!['AGREE', 'MAJORITY_AGREE'].includes(String(consensus))) throw new Error('The finalized consensus outcome is not verified.');
    const sender = receipt.sender ?? receipt.from_address;
    const recipient = receipt.recipient ?? receipt.to_address;
    if (sender?.toLowerCase() !== pending.account.toLowerCase() || recipient?.toLowerCase() !== pending.contract.toLowerCase()) throw new Error('Transaction sender or contract binding is not verified.');
    const method = pending.method as WriteMethod;
    onState?.({ hash: pending.hash, stage: 'VERIFYING_READBACK', message: 'Execution verified. Checking the contract result.' });
    let result: unknown;
    if (method === 'create_change') {
      const id = pending.context.candidateId;
      if (!id || !/^\d+$/.test(id) || pending.args.length !== 3) throw new Error('Create readback context is incomplete.');
      const row = await readView('get_change', [BigInt(id)]) as unknown as Parameters<typeof verifyCreate>[2];
      const counts = await readView('get_counts') as unknown as { change_count: string };
      verifyCreate(id, counts.change_count, row, { account: pending.account, uri: pending.args[0].value, revision: pending.args[1].value, deadline: pending.args[2].value });
      result = row;
    } else {
      const before = JSON.parse(pending.context.before) as ProposalSnapshot;
      const id = BigInt(pending.args[0].value);
      const row = await readView('get_change', [id]) as unknown as ProposalSnapshot;
      const page = await readView('get_events', [id, BigInt(before.event_count), 1n]) as unknown as { items: { actor: string; action: string; state: string; verdict: string }[] };
      if (page.items.length !== 1) throw new Error('The exact action event is unavailable.');
      verifyTransition(method, before, row, page.items[0], pending.account, pending.args[1]?.value);
      result = row;
    }
    clearVerifiedPending();
    onState?.({ hash: pending.hash, stage: 'SUCCESS', message: 'Finality, execution, consensus and contract result verified.' });
    return result;
  } catch (cause) {
    onState?.({ hash: pending.hash, stage: terminalFailure ? 'FAILED' : 'RECONCILIATION_REQUIRED', message: terminalFailure ? 'The transaction finalized, but execution did not succeed.' : 'Result verification is incomplete. Keep this transaction hash and continue verification.' });
    throw cause;
  } finally { active = false; }
}
