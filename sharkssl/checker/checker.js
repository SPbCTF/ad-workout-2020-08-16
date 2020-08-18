#!/usr/bin/env node
const superagent = require('superagent');
const { nanoid } = require('nanoid/non-secure');
const rs = require('jsrsasign');

const [OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR] = [101, 102, 103, 104, 110];

const CURVE = 'secp256k1';
const SIGN_ALG = 'SHA256withECDSA';
const TLDS = ['space', 'xyz', 'ooo', 'bar', 'by'];

function randStr(n = 10) {
  return nanoid(n);
}

Array.prototype.choose = function () {
  const index = Math.floor(Math.random() * this.length);
  return this[index];
};

function exitWith(code, public, private) {
  if (public) {
    console.log(public);
  }
  if (private) {
    if (private.status || private.response) {
      console.error(private.message);
      console.error(private.status);
      console.error(private.response.body);
    } else {
      console.error(private);
    }
  }
  process.exit(code);
}

function error(err) {
  if (err.code === 'ECONNREFUSED' || err.code === 'ECONNRESET ' || err.code === 'ETIMEDOUT') {
    exitWith(DOWN, "Can't connect", err);
  } else if (err.status || err.response) {
    if (err.response.body) {
      exitWith(MUMBLE, `${err.status}: ${err.response.body.error}`, err);
    } else {
      exitWith(MUMBLE, err.status, err);
    }
  } else {
    exitWith(MUMBLE, err, err);
  }
}

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
    const key = new rs.KJUR.crypto.ECDSA({ cuve: CURVE });
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

async function check(host) {
  let resp;
  const client = new Client(`http://${host}:3000`);

  const username = `${randStr()}.${TLDS.choose()}`;
  console.error(`username: ${username}`);

  try {
    resp = await client.signup(username);
    console.error(resp.body);
    const { cert, priv } = resp.body;

    resp = await client.login(cert, priv);
    console.error(resp.body);

    resp = await client.users();
    const users = resp.body;
    if (!users.find((x) => x.username === username)) {
      error("Can't find myself in users");
    }

    resp = await client.notes();
    console.error(resp.body);
    let notes = resp.body;
    if (notes.length !== 0) {
      error('Notes should be empty on new user');
    }

    const name = randStr(4);
    const text = randStr(8);

    resp = await client.notePut(name, text);
    console.error(resp.body);
    const { id } = resp.body;
    if (!id) {
      error('Got no id on new note');
    }

    resp = await client.notes();
    console.error(resp.body);
    notes = resp.body;

    if (notes.length !== 1 || notes[0].uuid !== id || notes[0].text !== text) {
      error('No new note created');
    }

    resp = await client.note(id);
    console.error(resp.body);
    const note = resp.body;

    if (note.name !== name || note.text !== text) {
      error('Got wrong name or text after creating new note');
    }

    process.exit(OK);
  } catch (err) {
    error(err);
  }
}

async function put(host, flagId, flag, vuln) {
  let resp;
  const client = new Client(`http://${host}:3000`);

  const username = `${randStr()}.${TLDS.choose()}`;
  console.error(`username: ${username}`);

  try {
    resp = await client.signup(username);
    console.error(resp.body);
    const { cert, priv } = resp.body;

    resp = await client.login(cert, priv);
    console.error(resp.body);

    const name = randStr(4);
    const text = flag;

    resp = await client.notePut(name, text);
    console.error(resp.body);
    const { id } = resp.body;
    if (!id) {
      error('Got no id on new note');
    }

    const newFlagId = [cert, priv, id];
    process.stdout.write(Buffer.from(JSON.stringify(newFlagId)).toString('base64'));
    process.exit(OK);
  } catch (err) {
    error(err);
  }
}

async function get(host, flagId, flag, vuln) {
  let resp;
  const client = new Client(`http://${host}:3000`);

  if (flagId.length === 14) {
    exitWith(CORRUPT, "Couldn't put, so failed on get");
  }

  const [cert, priv, id] = JSON.parse(Buffer.from(flagId, 'base64').toString('ascii'));

  try {
    resp = await client.login(cert, priv);
    console.error(resp.body);

    resp = await client.note(id);
    console.error(resp.body);
    const note = resp.body;

    if (!note) {
      exitWith(CORRUPT, "Can't get note", note);
    }

    if (note.text !== flag) {
      exitWith(CORRUPT, 'Got wrong text in note', note);
    }

    process.exit(OK);
  } catch (err) {
    error(err);
  }
}

const Checker = {
  check,
  put,
  get,
};

async function main() {
  const [mode, ...args] = process.argv.slice(2);
  let func = Checker[mode];
  if (!func) exitWith(CHECKER_ERROR.null, process.argv);

  func(...args).catch(errorHandler);
}

function errorHandler(err) {
  exitWith(CHECKER_ERROR, null, err);
}

process.on('unhandledRejection', errorHandler);
process.on('uncaughtException', errorHandler);

main().catch(errorHandler);
