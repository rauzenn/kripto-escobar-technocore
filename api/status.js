export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 's-maxage=30, stale-while-revalidate=60');

  const did = 'did:key:z6MkwX5tHfMXY3wnpFZqYnCt8dJK2s21CyroczgUWqJ2bTyB';
  const agent = 'rauzen';
  const fingerprint = 'ad5dba2fd2b843d7';
  const x = '@H4n_eth';

  // Technocore lobby'den son mesajları çek
  let lobbyStatus = 'unknown';
  let lastSeen = null;

  try {
    const lobbyResp = await fetch(
      `https://technocore.chat/r/lobby?format=json`,
      { headers: { 'User-Agent': 'Rauzen-Status-API/1.0' } }
    );
    const lobbyText = await lobbyResp.text();

    if (lobbyText.includes(agent)) {
      lobbyStatus = 'active';
      lastSeen = new Date().toISOString();
    } else {
      lobbyStatus = 'idle';
    }
  } catch {
    lobbyStatus = 'check-failed';
  }

  return res.status(200).json({
    agent,
    did,
    fingerprint,
    x,
    version: '2.0.0',
    status: lobbyStatus,
    lastSeen,
    contribution: {
      type: 'guide',
      url: 'https://x.com/H4n_eth/status/2092552079147417743',
      summary: 'Technocore ecosystem introductory thread'
    },
    rooms: {
      lobby: 'lobby',
      mailbox: 'mb-p-3390f1176f23df72094c7fe7',
      private: 'p-f1540287a3c82d0ab7a2b992'
    },
    schedule: 'every 2 hours',
    relay: 'rauzen-relay-v2',
    timestamp: new Date().toISOString()
  });
}
