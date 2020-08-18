/*
Client for communicating with service
*/
const superagent = require('superagent');

const CURVE = 'secp256k1';
const SIGN_ALG = 'SHA256withECDSA';

class Client {
  constructor(url) {
    this.url = url;
    // No cookie jar, pozor
    // this.agent = axios.create({
    //   baseURL: url,
    // });
    this.agent = superagent.agent();
  }

  async signup(username) {
    return this.agent.post(this.url + '/signup').send({
      username,
    });
  }

  async challenge(cert) {
    return this.agent.post(this.url + '/challenge').send({
      certificate: cert,
    });
  }

  async login(cert, priv) {
    const key = new rs.KJUR.crypto.ECDSA({ curve: CURVE });
    console.error(rs.pemtohex(priv));
    key.readPKCS8PrvKeyHex(rs.pemtohex(priv));

    const { challenge } = (await this.challenge(cert)).body;
    console.error(`Received challenge ${challenge}`);

    const sig = new rs.KJUR.crypto.Signature({ alg: SIGN_ALG });
    sig.init(priv);
    sig.updateHex(challenge);
    const response = sig.sign();

    return this.agent.post(this.url + '/login').send({
      challenge,
      response,
    });
  }

  async users() {
    return this.agent.get(this.url + '/users');
  }

  async notes() {
    return this.agent.get(this.url + '/notes');
  }

  async note(id) {
    return this.agent.get(this.url + '/note/' + id);
  }

  async notePut(name, text) {
    return this.agent.put(this.url + '/note').send({
      name,
      text,
    });
  }
}

module.exports = {
  Client,
  CURVE,
  SIGN_ALG,
};
