import { describe, expect, it } from 'vitest';
import { verifyCreate, verifyTransition, type ProposalSnapshot } from './readback';
const account = `0x${'1'.repeat(40)}`;
const before: ProposalSnapshot = { proposal_id: '7', state: 'ACTIVATABLE', verdict: 'COMPATIBLE', event_count: '5', attempt_count: '1', snapshot_version: '5', graph_digest: 'a'.repeat(64), consumers: ['consumer-a'] };
const after = { ...before, state: 'ACTIVATED', event_count: '6', snapshot_version: '6' };
const event = { actor: account, action: 'ACTIVATE', state: 'ACTIVATED', verdict: 'COMPATIBLE' };
describe('method-specific transition readback', () => {
  it('binds create to exact inputs and rejects concurrent count changes', () => {
    const uri = `https://github.com/a/b/blob/${'a'.repeat(40)}/change.md`;
    const expected = { account, uri, revision: 'a'.repeat(40), deadline: '1790000000' };
    const created = { ...before, state: 'DRAFT', event_count: '1', snapshot_version: '1', maintainer: account, uri: `https://raw.githubusercontent.com/a/b/${'a'.repeat(40)}/change.md`, revision: expected.revision, deadline: expected.deadline };
    expect(() => verifyCreate('7', '8', created, expected)).not.toThrow();
    expect(() => verifyCreate('7', '9', created, expected)).toThrow('identity');
    expect(() => verifyCreate('7', '8', { ...created, revision: 'b'.repeat(40) }, expected)).toThrow('identity');
    expect(() => verifyCreate('7', '8', { ...created, maintainer: `0x${'2'.repeat(40)}` }, expected)).toThrow('identity');
  });
  it('accepts a bound activation', () => expect(() => verifyTransition('activate_change', before, after, event, account)).not.toThrow());
  it('rejects different actors, actions, proposals and intervening writes', () => {
    expect(() => verifyTransition('activate_change', before, after, { ...event, actor: `0x${'2'.repeat(40)}` }, account)).toThrow();
    expect(() => verifyTransition('activate_change', before, after, { ...event, action: 'CREATE' }, account)).toThrow();
    expect(() => verifyTransition('activate_change', before, { ...after, proposal_id: '8' }, event, account)).toThrow();
    expect(() => verifyTransition('activate_change', before, { ...after, event_count: '7' }, event, account)).toThrow();
  });
  it('does not accept a finalized but wrong business state', () => {
    const wrong = { ...after, state: 'LOCKED' };
    expect(() => verifyTransition('activate_change', before, wrong, { ...event, state: 'LOCKED' }, account)).toThrow('does not prove');
  });
});
