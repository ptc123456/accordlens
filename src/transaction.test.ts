import { describe, expect, it } from 'vitest';
import { classifyTransaction } from './transaction';

describe('preview transaction truth boundary', () => {
  it('does not mistake an EVM success receipt for GenLayer finality', () => {
    expect(classifyTransaction({ status: 'success' })).toMatchObject({ finalized: false, success: false });
  });
  it('does not infer semantic success from FINALIZED alone', () => {
    expect(classifyTransaction({ statusName: 'FINALIZED' })).toMatchObject({ finalized: true, success: false });
  });
  it('requires finalized successful execution', () => {
    expect(classifyTransaction({ statusName: 'ACCEPTED', txExecutionResultName: 'FINISHED_WITH_RETURN' }).success).toBe(false);
    expect(classifyTransaction({ statusName: 'FINALIZED', txExecutionResultName: 'FINISHED_WITH_RETURN' })).toMatchObject({ finalized: true, success: true });
    expect(classifyTransaction({ statusName: 'FINALIZED', txExecutionResultName: 'NONDET_DISAGREE' }).success).toBe(false);
  });
});
