import { beforeEach, describe, expect, it, vi } from 'vitest';
const mocks = vi.hoisted(() => ({ finalized: vi.fn(), read: vi.fn(), pending: vi.fn(), clear: vi.fn() }));
vi.mock('./contract', () => ({ finalizedTransaction: mocks.finalized, readView: mocks.read }));
vi.mock('./recovery', () => ({ loadPending: mocks.pending, clearVerifiedPending: mocks.clear }));
import { reconcilePendingWrite } from './reconcile';
const account = `0x${'1'.repeat(40)}`;
const contract = `0x${'2'.repeat(40)}`;
beforeEach(() => {
  vi.clearAllMocks();
  mocks.pending.mockReturnValue({ method: 'create_change', account, contract, hash: `0x${'3'.repeat(64)}`, context: { candidateId: '0' }, args: [{ value: `https://raw.githubusercontent.com/a/b/${'a'.repeat(40)}/change.md` }, { value: 'a'.repeat(40) }, { value: '1790000000' }] });
  mocks.finalized.mockResolvedValue({ statusName: 'FINALIZED', lifecycle: 'finalized', txExecutionResultName: 'FINISHED_WITH_RETURN', resultName: 'MAJORITY_AGREE', sender: account, recipient: contract });
  mocks.read.mockImplementation(async (method: string) => method === 'get_counts' ? { change_count: '1' } : { proposal_id: '0', maintainer: account, uri: `https://raw.githubusercontent.com/a/b/${'a'.repeat(40)}/change.md`, revision: 'a'.repeat(40), deadline: '1790000000', state: 'DRAFT', event_count: '1', snapshot_version: '1' });
});
describe('single foreground and reload reconciliation', () => {
  it('unlocks only after finalized consensus, execution, binding and readback', async () => {
    await reconcilePendingWrite();
    expect(mocks.clear).toHaveBeenCalledTimes(1);
    expect(mocks.finalized).toHaveBeenCalledTimes(1);
  });
  it('retains the journal on wrong sender or consensus', async () => {
    mocks.finalized.mockResolvedValueOnce({ statusName: 'FINALIZED', txExecutionResultName: 'FINISHED_WITH_RETURN', resultName: 'MAJORITY_AGREE', sender: `0x${'4'.repeat(40)}`, recipient: contract });
    await expect(reconcilePendingWrite()).rejects.toThrow('binding');
    mocks.finalized.mockResolvedValueOnce({ statusName: 'FINALIZED', txExecutionResultName: 'FINISHED_WITH_RETURN', resultName: 'MAJORITY_DISAGREE', sender: account, recipient: contract });
    await expect(reconcilePendingWrite()).rejects.toThrow('consensus');
    expect(mocks.clear).not.toHaveBeenCalled();
  });
  it('retains the journal on unavailable readback or finality timeout', async () => {
    mocks.read.mockRejectedValueOnce(new Error('readback unavailable'));
    await expect(reconcilePendingWrite()).rejects.toThrow('readback unavailable');
    mocks.finalized.mockRejectedValueOnce(new Error('timeout'));
    await expect(reconcilePendingWrite()).rejects.toThrow('timeout');
    expect(mocks.clear).not.toHaveBeenCalled();
  });
});
