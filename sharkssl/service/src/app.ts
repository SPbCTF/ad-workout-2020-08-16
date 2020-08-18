import crypto from 'crypto';
import express from 'express';
import session from 'express-session';
import mongoStore from 'connect-mongo';
import asyncHandler from 'express-async-handler';
import morgan from 'morgan';
import mongo from 'mongodb';
import { nanoid } from 'nanoid/non-secure';

import { verifyResponse, genCertAndKey, privToPem } from './x509';

import { MONGO_URI } from '../config';
import { migrate } from './migrations';

const authRequired: express.Handler = (req, res, next) => {
  if (!req.username) {
    res.status(403).json({ error: 'Not authorized' });
    return;
  }
  return next();
};

function routes(app: express.Express): void {
  app.get('/', (req, res) => {
    res.status(200).send("Welcome to SharkSSL! No frontend == no problem!\nYou can't hack me!");
  });

  app.get('/ping', (req, res) => {
    return res.status(200).send('pong');
  });

  app.post(
    '/signup',
    asyncHandler(async (req, res) => {
      if (!req.body.username) {
        return res.status(400).json({ error: 'No username' });
      }

      const user = await app.db.collection('users').findOne({ username: req.body.username.toString() });
      if (user) {
        return res.status(400).json({ error: 'User already registred' });
      }

      const { cert, priv } = genCertAndKey(req.body.username.toString());
      const pem = cert.getPEMString();
      await app.db.collection('users').insertOne({ username: req.body.username.toString(), certificate: pem });

      res.json({ cert: pem, priv: privToPem(priv) });
    }),
  );

  app.post(
    '/challenge',
    asyncHandler(async (req, res) => {
      if (!req.body.certificate) {
        return res.status(400).json({ error: 'No certificate' });
      }

      const user = await app.db.collection('users').findOne({ certificate: req.body.certificate.toString() });
      if (!user) {
        return res.status(400).json({ error: 'Certificate not found' });
      }

      const challenge = crypto.randomBytes(16).toString('hex');
      await app.db.collection('challenges').insertOne({ challenge, userId: user._id });
      res.json({ challenge });
    }),
  );

  app.post(
    '/login',
    asyncHandler(async (req, res) => {
      if (!req.body.challenge) {
        return res.status(400).json({ error: 'No challenge' });
      }

      if (!req.body.response) {
        return res.status(400).json({ error: 'No response' });
      }

      const chall = await app.db.collection('challenges').findOne({ challenge: req.body.challenge.toString() });
      if (!chall) {
        return res.status(400).json({ error: 'Challenge not found' });
      }

      const user = await app.db.collection('users').findOne({ _id: chall.userId });
      if (!user) {
        return res.status(400).json({ error: 'User not found' });
      }

      if (!verifyResponse(user.certificate, chall.challenge, req.body.response)) {
        res.status(400).json({ error: 'Invalid signature' });
      } else {
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        req.session!.username = user.username;
        res.redirect('/');
      }
      await app.db.collection('challenges').deleteOne({ _id: chall._id });
    }),
  );

  app.get(
    '/users',
    asyncHandler(async (req, res) => {
      const users = await app.db
        .collection('users')
        .find(
          {},
          {
            projection: { _id: 0, username: 1, certificate: 1 },
            sort: {
              _id: -1,
            },
          },
        )
        .limit(100)
        .toArray();

      return res.json(users);
    }),
  );

  app.get(
    '/notes',
    authRequired,
    asyncHandler(async (req, res) => {
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

      res.json(notes);
    }),
  );
  app.get(
    '/note/:id',
    authRequired,
    asyncHandler(async (req, res) => {
      if (!req.params.id) {
        return res.status(400).json({ error: 'No id' });
      }

      const note = await app.db.collection('notes').findOne({ uuid: req.params.id });
      if (!note) {
        return res.status(404).json({ error: `Note with id ${req.params.id} not found` });
      }
      res.json({ id: note.id, name: note.name, text: note.text });
    }),
  );

  app.put(
    '/note',
    authRequired,
    asyncHandler(async (req, res) => {
      if (!req.body.name) {
        return res.status(400).json({ error: 'No name' });
      }

      if (!req.body.text) {
        return res.status(400).json({ error: 'No text' });
      }

      const note = {
        uuid: nanoid(),
        name: req.body.name.toString(),
        text: req.body.text.toString(),
        username: req.username,
      };
      await app.db.collection('notes').insertOne(note);
      res.status(201).json({ id: note.uuid });
    }),
  );
}

export async function createApp(): Promise<express.Express> {
  const app = express();

  app.use(morgan('dev'));
  app.use(express.json());

  const mongoClient = new mongo.MongoClient(MONGO_URI, { useUnifiedTopology: true, serverSelectionTimeoutMS: 2000 });
  await mongoClient.connect();
  console.log('mongo connected');

  app.mongo = mongoClient;
  app.db = mongoClient.db();

  await migrate(app.db);
  console.log('migrations done');

  const MongoStore = mongoStore(session);
  app.use(
    session({
      name: 'session',
      secret: 'kekkekkek',
      saveUninitialized: false,
      resave: false,
      store: new MongoStore({
        client: mongoClient,
        touchAfter: 5 * 60,
        autoRemove: 'native',
      }),
    }),
  );

  app.use((req, res, next) => {
    if (req.session?.username) {
      req.username = req.session.username;
    }
    return next();
  });

  routes(app);

  return app;
}

export async function tearDown(app: express.Express): Promise<void> {
  await app.mongo.close();
  console.log('mongo down');
}
