type RequestLike = { method?: string; body?: unknown };
type ResponseLike = { status: (code: number) => ResponseLike; setHeader: (name: string, value: string) => void; end: (body?: string) => void };

export default async function handler(request: RequestLike, response: ResponseLike) {
  response.setHeader('Access-Control-Allow-Origin', '*');
  response.setHeader('Access-Control-Allow-Headers', 'content-type');
  response.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  if (request.method === 'OPTIONS') { response.status(204).end(); return; }
  if (request.method !== 'POST') { response.status(405).end(JSON.stringify({ error: 'POST required' })); return; }
  try {
    const upstream = await fetch('https://studio-dev.genlayer.com/api', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(request.body ?? {}) });
    response.setHeader('content-type', upstream.headers.get('content-type') ?? 'application/json');
    response.status(upstream.status).end(await upstream.text());
  } catch { response.status(502).end(JSON.stringify({ error: 'Studio Dev is unavailable.' })); }
}
