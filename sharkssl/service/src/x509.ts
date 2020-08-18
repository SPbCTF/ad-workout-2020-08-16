import crypto from 'crypto';
import rs from 'jsrsasign'; // Worst API ever, sadly no other libs with x509 support and EC
import * as secp from '../lib/secp';

const CURVE = 'secp256k1';

function bytesToHex(uint8a: Uint8Array) {
  // pre-caching chars could speed this up 6x.
  let hex = '';
  for (let i = 0; i < uint8a.length; i++) {
    hex += uint8a[i].toString(16).padStart(2, '0');
  }
  return hex;
}

type KeyPair = {
  priv: rs.KJUR.crypto.ECDSA;
  pub: rs.KJUR.crypto.ECDSA;
  hpriv: string;
};

export function genKeyPair(): KeyPair {
  const privRaw = secp.utils.randomPrivateKey();
  const point = secp.Point.fromPrivateKey(privRaw);
  const pubRaw = point.toHex(false);

  const priv = rs.KEYUTIL.getKey({ d: bytesToHex(privRaw), curve: CURVE }) as rs.KJUR.crypto.ECDSA;
  const pub = new rs.KJUR.crypto.ECDSA({ curve: CURVE, pub: pubRaw });
  return { priv, pub, hpriv: bytesToHex(privRaw) };
}

export function genCertAndKey(cn: string): { cert: rs.KJUR.asn1.x509.Certificate } & Pick<KeyPair, 'priv' | 'hpriv'> {
  const { priv, pub, hpriv } = genKeyPair();
  console.error(pub.getPublicKeyXYHex());
  console.error(hpriv);
  console.error(priv);
  console.error(rs.KEYUTIL.getPEM(pub));
  const tbsc = new rs.KJUR.asn1.x509.TBSCertificate();

  tbsc.setSerialNumberByParam({ int: parseInt(crypto.randomBytes(4).toString('hex'), 16) });
  tbsc.setSignatureAlgByParam({ name: 'SHA256withECDSA' });
  tbsc.setNotBeforeByParam({ str: Math.trunc(Date.now() / 10) + 'Z' });
  const notAfter = new Date();
  notAfter.setFullYear(notAfter.getFullYear() + 1);
  tbsc.setNotAfterByParam({ str: Math.trunc(notAfter.getTime() / 10) + 'Z' });
  tbsc.setIssuerByParam({ str: `/C=RU/CN=${cn}` });
  tbsc.setSubjectByParam({ str: `/C=RU/CN=${cn}` });
  tbsc.setSubjectPublicKeyByGetKey(pub);

  // add extensions
  tbsc.appendExtension(new rs.KJUR.asn1.x509.KeyUsage({ bin: '11', critical: false }));

  const cert = new rs.KJUR.asn1.x509.Certificate({
    prvkeyobj: priv,
    tbscertobj: tbsc,
  });
  cert.sign();
  return { cert, priv, hpriv };
}

export function verifyResponse(cert: string, chall: string, resp: string): boolean {
  const sig = new rs.KJUR.crypto.Signature({ alg: 'SHA256withECDSA' });
  sig.init(cert);
  sig.updateHex(chall);
  return sig.verify(resp);
}

type getPem = (
  keyObjOrHex: rs.KJUR.crypto.ECDSA,
  formatType?: rs.PrivateKeyOutputFormatType,
  passwd?: string,
  encAlg?: string,
  hexType?: string,
  ivsaltHex?: string,
) => string;

// Lol, wrong types in @types
const getPemImpl: getPem = rs.KEYUTIL.getPEM as getPem;

// Docs are so cool, so I first used this code🤦‍♂️:
export function privHexToPem(raw: string, sep = '\n'): string {
  const data = Buffer.from(`302e0201010420${raw}a00706052b8104000a`).toString('base64');
  return `-----BEGIN EC PRIVATE KEY-----${sep}${data}${sep}-----END EC PRIVATE KEY-----${sep}`;
}

export function privToPem(priv: rs.KJUR.crypto.ECDSA): string {
  return getPemImpl(priv, 'PKCS8PRV');
}
