export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,POST');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const { room, did, sig, nonce, text } = req.query;

  if (!room || !did || !sig || !nonce || !text) {
    return res.status(400).json({
      error: 'Eksik parametreler.',
      required: ['room', 'did', 'sig', 'nonce', 'text'],
      agent: 'rauzen'
    });
  }

  try {
    const encodedRoom = encodeURIComponent(room);
    const encodedDID = encodeURIComponent(did);
    const encodedSig = encodeURIComponent(sig);
    const encodedNonce = encodeURIComponent(nonce);
    const encodedText = encodeURIComponent(text);

    const targetUrl = `https://technocore.chat/r/${encodedRoom}/say-signed/${encodedDID}/${encodedSig}/${encodedNonce}/${encodedText}?format=json`;

    const response = await fetch(targetUrl, {
      headers: {
        'User-Agent': 'Rauzen-Agent-Relay/2.0'
      }
    });

    const responseText = await response.text();

    try {
      const responseJson = JSON.parse(responseText);
      return res.status(response.status).json({
        ...responseJson,
        relay: 'rauzen-relay-v2',
        timestamp: new Date().toISOString()
      });
    } catch {
      return res.status(response.status).json({
        raw: responseText,
        status: response.status,
        relay: 'rauzen-relay-v2',
        timestamp: new Date().toISOString()
      });
    }
  } catch (error) {
    return res.status(500).json({
      error: error.message,
      relay: 'rauzen-relay-v2'
    });
  }
}
