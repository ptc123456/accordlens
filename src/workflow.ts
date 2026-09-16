export const WRITE_METHODS = {
  create_change: { label: 'Create proposal', fields: ['uri', 'revision', 'deadline'] },
  register_dependency: { label: 'Register consumer', fields: ['proposal', 'consumer', 'uri'] },
  lock_dependency_graph: { label: 'Lock dependency graph', fields: ['proposal'] },
  expire_change: { label: 'Expire draft', fields: ['proposal'] },
  evaluate_compatibility: { label: 'Evaluate compatibility', fields: ['proposal'] },
  acknowledge_condition: { label: 'Verify remediation', fields: ['proposal', 'consumer', 'uri'] },
  activate_change: { label: 'Activate proposal', fields: ['proposal'] },
} as const;
export type WriteMethod = keyof typeof WRITE_METHODS;
export function parseU256(value: string, label = 'Proposal number'): bigint {
  if (!/^(0|[1-9][0-9]*)$/.test(value)) throw new Error(`${label} must be a non-negative whole decimal number.`);
  const result = BigInt(value);
  if (result >= 2n ** 256n) throw new Error(`${label} exceeds the contract's integer range.`);
  return result;
}
export function workflowArgs(method: WriteMethod, input: Record<string, string>): (string | bigint)[] {
  return WRITE_METHODS[method].fields.map(field => {
    const value = input[field] ?? '';
    if (field === 'proposal' || field === 'deadline') return parseU256(value, field === 'deadline' ? 'Deadline' : 'Proposal number');
    if (field === 'consumer' && !/^[a-z][a-z0-9-]{0,47}$/.test(value)) throw new Error('Consumer ID must start with a lowercase letter and contain up to 48 lowercase letters, digits, or hyphens.');
    if (field === 'revision' && !/^[0-9a-f]{40}$/.test(value)) throw new Error('Revision must be the full 40-character lowercase Git commit.');
    if (field === 'uri' && (!value.startsWith('https://') || new TextEncoder().encode(value).length > 2048)) throw new Error('Use an immutable HTTPS GitHub document URL, at most 2,048 bytes.');
    return value;
  });
}
