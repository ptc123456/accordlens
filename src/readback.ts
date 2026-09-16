import type { WriteMethod } from './workflow';
export type ProposalSnapshot = { proposal_id: string; state: string; verdict: string; event_count: string; attempt_count: string; snapshot_version: string; graph_digest: string; consumers: string[] };
export function verifyCreate(candidateId: string, afterCount: string, row: ProposalSnapshot & { maintainer: string; uri: string; revision: string; deadline: string }, expected: { account: string; uri: string; revision: string; deadline: string }): void {
  const url = new URL(expected.uri);
  const parts = url.pathname.split('/');
  const normalized = url.hostname === 'github.com' && parts[3] === 'blob' ? `https://raw.githubusercontent.com/${parts[1]}/${parts[2]}/${parts.slice(4).join('/')}` : expected.uri;
  if (BigInt(afterCount) !== BigInt(candidateId) + 1n || row.proposal_id !== candidateId || row.maintainer.toLowerCase() !== expected.account.toLowerCase() || row.uri !== normalized || row.revision !== expected.revision || row.deadline !== expected.deadline || row.state !== 'DRAFT' || row.event_count !== '1' || row.snapshot_version !== '1') throw new Error('The created proposal identity is not proven or concurrent activity changed the snapshot. Keep this transaction for reconciliation.');
}
const actions: Record<Exclude<WriteMethod, 'create_change'>, string> = { register_dependency: 'REGISTER', lock_dependency_graph: 'LOCK', expire_change: 'EXPIRE', evaluate_compatibility: 'EVALUATE', acknowledge_condition: 'REMEDIATION', activate_change: 'ACTIVATE' };
export function verifyTransition(method: Exclude<WriteMethod, 'create_change'>, before: ProposalSnapshot, after: ProposalSnapshot, event: { actor: string; action: string; state: string; verdict: string }, account: string, consumer?: string): void {
  if (before.proposal_id !== after.proposal_id || BigInt(after.event_count) !== BigInt(before.event_count) + 1n || BigInt(after.snapshot_version) !== BigInt(before.snapshot_version) + 1n || event.actor.toLowerCase() !== account.toLowerCase() || event.action !== actions[method] || event.state !== after.state || event.verdict !== after.verdict) throw new Error('The authoritative action identity or snapshot changed. Keep this transaction for reconciliation.');
  const valid = method === 'activate_change' ? after.state === 'ACTIVATED'
    : method === 'expire_change' ? after.state === 'EXPIRED'
    : method === 'lock_dependency_graph' ? after.state === 'LOCKED' && /^[0-9a-f]{64}$/.test(after.graph_digest)
    : method === 'register_dependency' ? after.state === 'DRAFT' && Boolean(consumer && after.consumers.includes(consumer))
    : method === 'acknowledge_condition' ? ['REMEDIATION', 'ACTIVATABLE'].includes(after.state)
    : BigInt(after.attempt_count) === BigInt(before.attempt_count) + 1n && ({ COMPATIBLE: 'ACTIVATABLE', CONDITIONAL: 'REMEDIATION', INCOMPATIBLE: 'REJECTED', UNRESOLVED: 'LOCKED' } as Record<string, string>)[after.verdict] === after.state;
  if (!valid) throw new Error('The resulting contract state does not prove this action. Keep the transaction locked.');
}
