# sharkssl

@kabachook

Innovative service for storing notes without frontend and using novel TLS-like authentication

Language: TypeScript

## Deploy

```bash
docker-compose up -d --build
```

## Bugs

### Regex

When searching notes in MongoDB, application uses regex to match documents
which belong to authenticated user

Code at [`app.ts`](./service/src/app.ts):
```typescript
const notes = await app.db
      .collection('notes')
      .find(
        {
          username: {
            $regex: req.username,
          },
        },
        {
          projection: { _id: 0, uuid: 1, name: 1, text: 1 },
        },
      )
      .maxTimeMS(2000)
      .toArray();
```

Here we control `req.username`, so we can sign up using following username:
`.*space`

It will match all notes of users matching this regex

Due to x509 cert limitations we can't use `+`

Exploit: [`regex.js`](./sploits/src/regex.js)

Patch:
```typescript
.find(
        {
          username: req.username.toString(),
        },
        {
          projection: { _id: 0, uuid: 1, name: 1, text: 1 },
        },
      )
```

### Weak key generation

When generating private key for user, application uses `secp.utils.randomPrivateKey()`

Let's look at it:
```typescript
randomPrivateKey: (bytesLength = 4): Uint8Array => {
    if (typeof window == 'object' && 'crypto' in window) {
      return window.crypto.getRandomValues(new Uint8Array(bytesLength));
    } else if (typeof process === 'object' && 'node' in process.versions) {
      const { randomBytes } = require('crypto');
      return new Uint8Array(randomBytes(bytesLength).buffer);
    } else {
      throw new Error("The environment doesn't have randomBytes function");
    }
  },
```

There is some polyfill for browser, but what strage is `bytesLength = 4`.

So basically application generates weak ECDSA key, which can be retrieved
solving ECDLP problem.

There is an original library [noble-secp256k1](https://github.com/paulmillr/noble-secp256k1) (pretty good one!), so you can either diff the original source or look at the length of private keys in responses.

Exploit: [`weakKey.js`](./sploits/src/weakKey.js)

> You need to have Python and Sagemath installed

Patch:
```javascript
randomPrivateKey(32)
```