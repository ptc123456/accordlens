export const STUDIO_NEXT_CHAIN_ID = 61997;
export const STUDIO_NEXT_CHAIN_HEX = '0xf22d';
export const STUDIO_NEXT_RPC = 'https://studio-dev.genlayer.com/api';
export const STUDIO_NEXT_EXPLORER = 'https://explorer-studio-dev.genlayer.com';
export const CONTRACT_ADDRESS = (import.meta.env.VITE_CONTRACT_ADDRESS || '0xa687ba36bc5457b40e9F3b1Ed6AE167914F6AAF7') as string;
export const CONTRACT_ADDRESS_VALID = typeof CONTRACT_ADDRESS === 'string' && /^0x[0-9a-fA-F]{40}$/.test(CONTRACT_ADDRESS);
