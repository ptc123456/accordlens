export type WalletKind = 'MetaMask' | 'OKX Wallet' | 'Rabby';
export type WalletSession = { kind: WalletKind; account: `0x${string}`; chainId: string };
export type Eip1193 = {
  request(args: { method: string; params?: unknown[] }): Promise<unknown>;
  on?: (event: string, listener: (...args: unknown[]) => void) => void;
  removeListener?: (event: string, listener: (...args: unknown[]) => void) => void;
};
export type WalletInfo = { name?: string; rdns?: string; uuid?: string; icon?: string };
export type AnnouncedProvider = { info?: WalletInfo; provider: Eip1193 };
export type WalletPhase = 'DISCONNECTED' | 'DISCOVERING' | 'CHOOSER_OPEN' | 'CONNECTING' | 'CONNECTED' | 'WRONG_CHAIN' | 'ERROR';
export type WalletState = { phase: WalletPhase; wallets: AnnouncedProvider[]; selected: AnnouncedProvider | null; kind: WalletKind | null; account: `0x${string}` | null; error: string };
export const initialWalletState: WalletState = { phase: 'DISCONNECTED', wallets: [], selected: null, kind: null, account: null, error: '' };
export type WalletAction =
  | { type: 'DISCOVER'; wallets: AnnouncedProvider[] }
  | { type: 'OPEN' }
  | { type: 'CONNECT'; wallet: AnnouncedProvider }
  | { type: 'CONNECTED'; wallet: AnnouncedProvider; kind: WalletKind; account: `0x${string}` }
  | { type: 'ACCOUNT'; account: `0x${string}` }
  | { type: 'WRONG_CHAIN'; message: string }
  | { type: 'ERROR'; message: string }
  | { type: 'CLOSE' }
  | { type: 'DISCONNECT' };

export function walletReducer(state: WalletState, action: WalletAction): WalletState {
  if (action.type === 'DISCOVER') return { ...state, wallets: action.wallets, phase: state.phase === 'DISCOVERING' ? 'CHOOSER_OPEN' : state.phase };
  if (action.type === 'OPEN') return { ...state, phase: state.wallets.length ? 'CHOOSER_OPEN' : 'DISCOVERING', error: '' };
  if (action.type === 'CONNECT') return { ...state, phase: 'CONNECTING', selected: action.wallet, kind: walletName(action.wallet), account: null, error: '' };
  if (action.type === 'CONNECTED') return { ...state, phase: 'CONNECTED', selected: action.wallet, kind: action.kind, account: action.account, error: '' };
  if (action.type === 'ACCOUNT') return state.selected && state.kind ? { ...state, phase: 'CONNECTED', account: action.account, error: '' } : initialWalletState;
  if (action.type === 'WRONG_CHAIN') return { ...state, phase: 'WRONG_CHAIN', account: null, error: action.message };
  if (action.type === 'ERROR') return { ...state, phase: 'ERROR', account: null, error: action.message };
  if (action.type === 'CLOSE') return state.phase === 'CONNECTED' ? state : { ...state, phase: 'DISCONNECTED' };
  return { ...initialWalletState, wallets: state.wallets };
}

const canonical: Record<WalletKind, { rdns: string[]; names: string[] }> = {
  MetaMask: { rdns: ['io.metamask'], names: ['metamask'] },
  'OKX Wallet': { rdns: ['com.okex.wallet', 'com.okx.wallet'], names: ['okx wallet', 'okx'] },
  Rabby: { rdns: ['io.rabby'], names: ['rabby'] },
};
function normalized(value: string | undefined): string { return (value ?? '').trim().toLowerCase(); }
export function walletName(item: AnnouncedProvider): WalletKind | null {
  const rdns = normalized(item.info?.rdns); const name = normalized(item.info?.name);
  return (Object.keys(canonical) as WalletKind[]).find(kind => canonical[kind].rdns.includes(rdns) || canonical[kind].names.includes(name)) ?? null;
}
export function discoverWallets(items: AnnouncedProvider[]): AnnouncedProvider[] {
  const providers = new Set<Eip1193>(); const kinds = new Set<WalletKind>();
  return items.filter(item => { const kind = walletName(item); if (!kind || providers.has(item.provider) || kinds.has(kind)) return false; providers.add(item.provider); kinds.add(kind); return true; });
}
export function mergeWallet(current: AnnouncedProvider[], incoming: AnnouncedProvider, preferIncoming = true): AnnouncedProvider[] {
  const kind = walletName(incoming); if (!kind) return current;
  const withoutDuplicates = current.filter(item => item.provider !== incoming.provider && walletName(item) !== kind && (!incoming.info?.uuid || item.info?.uuid !== incoming.info.uuid));
  if (!preferIncoming && withoutDuplicates.length !== current.length) return current;
  return discoverWallets([...withoutDuplicates, incoming]);
}
export function walletInitial(kind: WalletKind): string { return kind === 'MetaMask' ? 'M' : kind === 'Rabby' ? 'R' : 'O'; }
export function disconnectedAfterReload(): null { return null; }
export function validSession(value: unknown, expectedChain = '0xf22d'): value is WalletSession {
  if (!value || typeof value !== 'object') return false;
  const x = value as Record<string, unknown>;
  return typeof x.account === 'string' && /^0x[0-9a-fA-F]{40}$/.test(x.account) && typeof x.chainId === 'string' && x.chainId.toLowerCase() === expectedChain.toLowerCase() && typeof x.kind === 'string' && (Object.keys(canonical) as string[]).includes(x.kind);
}
export function announceWallets(onChange: (wallets: AnnouncedProvider[]) => void): () => void {
  let found: AnnouncedProvider[] = [];
  const announce = (event: Event) => { const detail = (event as CustomEvent<AnnouncedProvider>).detail; if (detail?.provider) { found = mergeWallet(found, detail, true); onChange(found); } };
  window.addEventListener('eip6963:announceProvider', announce);
  window.dispatchEvent(new Event('eip6963:requestProvider'));
  const timer = window.setTimeout(() => {
    const ethereum = (window as Window & { ethereum?: Eip1193 & { providers?: Eip1193[]; isMetaMask?: boolean; isRabby?: boolean; isOkxWallet?: boolean } }).ethereum;
    const providers = ethereum?.providers?.length ? ethereum.providers : ethereum ? [ethereum] : [];
    for (const provider of providers) {
      const flags = provider as Eip1193 & { isMetaMask?: boolean; isRabby?: boolean; isOkxWallet?: boolean };
      const kind: WalletKind | null = flags.isRabby ? 'Rabby' : flags.isOkxWallet ? 'OKX Wallet' : flags.isMetaMask ? 'MetaMask' : null;
      if (kind) found = mergeWallet(found, { info: { name: kind }, provider }, false);
    }
    onChange(discoverWallets(found));
  }, 250);
  return () => { window.clearTimeout(timer); window.removeEventListener('eip6963:announceProvider', announce); };
}
