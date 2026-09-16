import { useEffect, useState } from 'react';
import { loadPending, type PendingWrite } from './recovery';

function snapshot(): { pending?: PendingWrite; error?: string } {
  try { return { pending: loadPending() }; }
  catch { return { error: 'An earlier wallet request could not be read. Restore transaction storage before submitting again.' }; }
}
export function RecoveryPanel({ refresh, automatic = false }: { refresh?: string; automatic?: boolean }) {
  const [record, setRecord] = useState(snapshot);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  useEffect(() => { setRecord(snapshot()); setMessage(''); }, [refresh]);
  if (record.error) return <section className="error" role="alert">{record.error}</section>;
  if (!record.pending) return message ? <p className="recovery-note" role="status">{message}</p> : null;
  const pending = record.pending;
  async function verify() {
    if (!pending.hash || busy) return;
    setBusy(true);
    setMessage('Checking the existing transaction. No new transaction will be submitted.');
    try {
      const { reconcilePendingWrite } = await import('./reconcile');
      await reconcilePendingWrite();
      setMessage('Finality, successful execution and authoritative result verified. The request is complete.');
      setRecord(snapshot());
    } catch { setMessage('Verification is interrupted. The existing request remains locked; do not resubmit.'); }
    finally { setBusy(false); }
  }
  return <section className="recovery-note" aria-label="Transaction recovery">
    <h3>Continue an existing request</h3>
    <p>Your {pending.method.replace(/_/g, ' ')} request is retained for account {pending.account.slice(0, 6)}…{pending.account.slice(-4)}. No new write is needed to check it.</p>
    {pending.hash ? <><code style={{ overflowWrap: 'anywhere' }}>{pending.hash}</code>{automatic ? <p role="status">Automatic verification is already in progress.</p> : <p><button type="button" disabled={busy} onClick={verify}>{busy ? 'Verifying…' : 'Continue verification'}</button></p>}</> : <p>The wallet response is uncertain and no hash was received. Check the wallet activity for this request; do not submit another one.</p>}
    {message && <p role="status" aria-live="polite">{message}</p>}
  </section>;
}
