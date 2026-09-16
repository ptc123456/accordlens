import { describe, expect, it } from 'vitest';
import { parseU256, workflowArgs, WRITE_METHODS } from './workflow';
describe('contract workflow argument mapping', () => {
  it('preserves the exact seven-write surface', () => {
    expect(Object.keys(WRITE_METHODS)).toHaveLength(7);
    expect(workflowArgs('create_change', { uri: 'https://github.com/a/b/blob/' + 'a'.repeat(40) + '/change.md', revision: 'a'.repeat(40), deadline: '1790000000' })).toHaveLength(3);
    for (const method of ['lock_dependency_graph', 'expire_change', 'evaluate_compatibility', 'activate_change'] as const) expect(workflowArgs(method, { proposal: '9007199254740993' })).toEqual([9007199254740993n]);
    for (const method of ['register_dependency', 'acknowledge_condition'] as const) expect(workflowArgs(method, { proposal: '0', consumer: 'consumer-a', uri: 'https://github.com/a/b/blob/' + 'a'.repeat(40) + '/constraint.md' })).toEqual([0n, 'consumer-a', 'https://github.com/a/b/blob/' + 'a'.repeat(40) + '/constraint.md']);
  });
  it('rejects lossy, exponential, empty, negative and overflow IDs', () => {
    for (const value of ['', '1e3', '-1', '1.5', '01', ' 1', (2n ** 256n).toString()]) expect(() => parseU256(value)).toThrow();
    expect(parseU256((2n ** 256n - 1n).toString())).toBe(2n ** 256n - 1n);
  });
  it('rejects malformed consumer identities', () => {
    for (const consumer of ['', 'Consumer', 'a_b', 'a'.repeat(49)]) expect(() => workflowArgs('register_dependency', { proposal: '0', consumer, uri: 'https://github.com/a/b' })).toThrow('Consumer ID');
  });
});
