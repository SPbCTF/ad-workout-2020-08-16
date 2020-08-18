const { Client } = require('./client');

const host = process.argv[2];

function signedUp(host) {
  // Implement username memoization
  return false;
}

function getCreds(host) {
  // Implement creds cache
}

async function main() {
  let resp, cert, priv;
  const client = new Client(`http://${host}:3000`);

  // Register once and store creds in some cache
  // or create modifications for regex on each signup
  const username = `.*space`;

  console.error(`username: ${username}`);

  if (!signedUp(host)) {
    resp = await client.signup(username);
    cert = resp.body.cert;
    priv = resp.body.priv;
  } else {
    const creds = getCreds(host);
    cert = creds.cert;
    priv = creds.priv;
  }

  resp = await client.login(cert, priv);

  resp = await client.notes();
  console.error(resp.body);
  let notes = resp.body;

  // Got all notes from users mathing regex in username
  console.log(notes);
}

main();
