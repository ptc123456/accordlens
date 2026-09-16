import { useState } from 'react';
import { WRITE_METHODS, workflowArgs, type WriteMethod } from './workflow';
import type { AnnouncedProvider } from './wallet';
import type { ProposalSnapshot } from './readback';
import type { TransactionState } from './transaction';

type ExistingMethod = Exclude<WriteMethod, 'create_change'>;
export function WorkflowPanel({ provider, account, onState }: { provider: AnnouncedProvider | null; account: string | null; onState: (value: TransactionState) => void }) {
  const [method, setMethod] = useState<ExistingMethod>('register_dependency');
  const [input, setInput] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState('');
  async function execute(event: React.FormEvent) {
    event.preventDefault(); setError(''); setResult('');
    if (!provider || !account) { setError('Connect your chosen wallet before submitting this action.'); return; }
    setBusy(true);
    try {
      const args = workflowArgs(method, input);
      const [{ readView }, { submitWrite }, { reconcilePendingWrite }] = await Promise.all([import('./contract'), import('./transaction'), import('./reconcile')]);
      const before = await readView('get_change', [args[0]]) as unknown as ProposalSnapshot;
      await submitWrite(provider, account as `0x${string}`, method, args, onState, { before: JSON.stringify(before) });
      const after = await reconcilePendingWrite(onState);
      setResult(JSON.stringify(after, null, 2));
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'The action could not be verified. Do not resubmit an uncertain request.'); }
    finally { setBusy(false); }
  }
  return <section className="panel"><div className="panel-head"><h2>Continue a proposal</h2></div><form className="create-form" onSubmit={execute}>
    <label>Action<select value={method} disabled={busy} onChange={event => { setMethod(event.target.value as ExistingMethod); setError(''); setResult(''); }}>{(Object.keys(WRITE_METHODS) as WriteMethod[]).filter(value => value !== 'create_change').map(value => <option key={value} value={value}>{WRITE_METHODS[value].label}</option>)}</select></label>
    {WRITE_METHODS[method].fields.map(field => <label key={field}>{field === 'proposal' ? 'Proposal number' : field === 'consumer' ? 'Consumer ID' : 'Immutable document URL'}<input name={field} value={input[field] ?? ''} disabled={busy} onChange={event => setInput({ ...input, [field]: event.target.value })} required /></label>)}
    <button disabled={busy || !account}>{busy ? 'Verifying action…' : `Sign ${WRITE_METHODS[method].label.toLowerCase()}`}</button>
  </form>{error && <p className="error" role="alert">{error}</p>}{result && <><p role="status">Finalized execution and authoritative transition verified.</p><pre className="readback">{result}</pre></>}</section>;
}
