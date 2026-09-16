import { describe, expect, it } from 'vitest';
import { requireChain, RpcError } from './rpc';
describe('rpc boundary',()=>{it('accepts Studio Dev chain 61997',async()=>await expect(requireChain({request:async()=> '0xf22d' as never})).resolves.toBeUndefined());it('rejects another chain',async()=>await expect(requireChain({request:async()=> '0xf22f' as never})).rejects.toMatchObject({code:'WRONG_NETWORK'}));it('normalizes failures',async()=>await expect(requireChain({request:async()=>{throw new Error('down')}})).rejects.toBeInstanceOf(RpcError))});
