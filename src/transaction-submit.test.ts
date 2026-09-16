import { beforeEach, describe, expect, it, vi } from 'vitest';
const mocks = vi.hoisted(() => ({ estimate: vi.fn(), write: vi.fn() }));
vi.mock('./contract', () => ({ providerClient: () => ({ estimateTransactionFeesForWrite: mocks.estimate, writeContract: mocks.write }) }));
vi.mock('./config', () => ({ CONTRACT_ADDRESS: `0x${'2'.repeat(40)}`, CONTRACT_ADDRESS_VALID: true, STUDIO_NEXT_CHAIN_HEX: '0xf22d', STUDIO_NEXT_CHAIN_ID: 61997 }));
import { submitWrite } from './transaction';
import { clearVerifiedPending, loadPending } from './recovery';
const account = `0x${'1'.repeat(40)}` as const;
const hash = `0x${'3'.repeat(64)}`;
function provider(chain = '0xf22d', balance = '0x64', active = account) {
  return { request: vi.fn(async ({ method }: { method: string }) => method === 'eth_chainId' ? chain : method === 'eth_accounts' ? [active] : balance) };
}
beforeEach(() => {
  vi.clearAllMocks();
  mocks.estimate.mockResolvedValue({ feeValue: 10n, distribution: { appealRounds: 0n } });
  mocks.write.mockResolvedValue(hash);
  const data = new Map<string, string>();
  vi.stubGlobal('localStorage', { getItem: (key: string) => data.get(key) ?? null, setItem: (key: string, value: string) => data.set(key, value), removeItem: (key: string) => data.delete(key) });
  clearVerifiedPending();
});
describe('preview submission guards', () => {
  it('rejects the historical chain without broadcasting', async () => {
    await expect(submitWrite({ provider: provider('0xf22f') }, account, 'activate_change', [0n], vi.fn())).rejects.toThrow('GenLayer Studio Dev');
    expect(mocks.write).not.toHaveBeenCalled();
  });
  it('rejects changed accounts and insufficient balances', async () => {
    await expect(submitWrite({ provider: provider('0xf22d', '0x64', `0x${'4'.repeat(40)}`) }, account, 'activate_change', [0n], vi.fn())).rejects.toThrow('account changed');
    await expect(submitWrite({ provider: provider('0xf22d', '0x1') }, account, 'activate_change', [0n], vi.fn())).rejects.toThrow('insufficient GEN');
    expect(mocks.write).not.toHaveBeenCalled();
  });
  it('attaches the estimated method fee and retains one returned hash', async () => {
    const state = vi.fn();
    await expect(submitWrite({ provider: provider() }, account, 'activate_change', [0n], state)).resolves.toBe(hash);
    expect(mocks.estimate).toHaveBeenCalledTimes(1);
    expect(mocks.write).toHaveBeenCalledTimes(1);
    expect(mocks.write.mock.calls[0][0].fees.feeValue).toBe(10n);
    expect(state).toHaveBeenLastCalledWith(expect.objectContaining({ hash, stage: 'WAITING_FOR_FINALITY' }));
    expect(loadPending()?.hash).toBe(hash);
    await expect(submitWrite({ provider: provider() }, account, 'activate_change', [0n], state)).rejects.toThrow('Do not submit again');
    expect(mocks.write).toHaveBeenCalledTimes(1);
  });
  it('retains the pre-hash lock after an ambiguous wallet failure', async () => {
    mocks.write.mockRejectedValue(new Error('transport lost'));
    await expect(submitWrite({ provider: provider() }, account, 'activate_change', [0n], vi.fn())).rejects.toThrow('transport lost');
    expect(loadPending()).toMatchObject({ method: 'activate_change', account });
    await expect(submitWrite({ provider: provider() }, account, 'activate_change', [0n], vi.fn())).rejects.toThrow('Do not submit again');
    expect(mocks.write).toHaveBeenCalledTimes(1);
  });
  it('unlocks only a verified wallet rejection before hash', async () => {
    const state = vi.fn(); mocks.write.mockRejectedValue({ code: 4001 });
    await expect(submitWrite({ provider: provider() }, account, 'activate_change', [0n], state)).rejects.toMatchObject({ code: 4001 });
    expect(loadPending()).toBeUndefined();
    expect(state).toHaveBeenLastCalledWith(expect.objectContaining({ stage: 'REJECTED' }));
  });
  it('closes the double-click window before the wallet returns a hash', async () => {
    let resolveEstimate!: (value: unknown) => void;
    mocks.estimate.mockImplementationOnce(() => new Promise(resolve => { resolveEstimate = resolve; }));
    const first = submitWrite({ provider: provider() }, account, 'activate_change', [0n], vi.fn());
    await expect(submitWrite({ provider: provider() }, account, 'activate_change', [0n], vi.fn())).rejects.toThrow('Do not submit again');
    resolveEstimate({ feeValue: 10n, distribution: { appealRounds: 0n } });
    await expect(first).resolves.toBe(hash);
    expect(mocks.write).toHaveBeenCalledTimes(1);
  });
});
