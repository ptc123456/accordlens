export type Rpc = { request<T = unknown>(method: string, params?: unknown[]): Promise<T> };
export class RpcError extends Error { constructor(public code: string, message: string) { super(message); } }
export async function call<T>(rpc: Rpc, method: string, params: unknown[] = []): Promise<T> {
  try { return await rpc.request<T>(method, params); }
  catch (error) { throw new RpcError('RPC_FAILURE', error instanceof Error ? error.message : 'RPC request failed'); }
}
export async function requireChain(rpc: Rpc, expected = '0xf22d'): Promise<void> {
  const actual = await call<unknown>(rpc, 'eth_chainId');
  if (typeof actual !== 'string' || actual.toLowerCase() !== expected.toLowerCase()) throw new RpcError('WRONG_NETWORK', `Expected ${expected}, got ${String(actual)}`);
}
