import { renderToStaticMarkup } from 'react-dom/server';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const pending = vi.hoisted(() => vi.fn());
vi.mock('./recovery', () => ({ loadPending: pending }));
import { RecoveryPanel } from './RecoveryPanel';

beforeEach(() => pending.mockReturnValue({
  method: 'create_change', account: `0x${'1'.repeat(40)}`, contract: `0x${'2'.repeat(40)}`,
  hash: `0x${'3'.repeat(64)}`, args: [], context: {}
}));

describe('transaction recovery controls', () => {
  it('does not offer concurrent manual verification while automatic verification is active', () => {
    const html = renderToStaticMarkup(<RecoveryPanel automatic />);
    expect(html).toContain('Automatic verification is already in progress.');
    expect(html).not.toContain('Continue verification');
  });

  it('offers manual recovery when no automatic verification is active', () => {
    expect(renderToStaticMarkup(<RecoveryPanel />)).toContain('Continue verification');
  });
});
