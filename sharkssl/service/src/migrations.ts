import { Db } from 'mongodb';

export const indices = [
  {
    collection: 'users',
    fields: { username: 1 },
  },
  {
    collection: 'users',
    fields: { certificate: 1 },
  },
  {
    collection: 'challenges',
    fields: { challenge: 1 },
  },
  {
    collection: 'notes',
    fields: { username: 1 },
  },
  {
    collection: 'notes',
    fields: { uuid: 1 },
  },
];

export async function migrate(db: Db): Promise<void> {
  const collections = await db.listCollections().toArray();
  for (const index of indices) {
    const name = `${index.collection}_${Object.keys(index.fields).join('_')}`;

    if (collections.find((x) => x.name === index.collection)) {
      const indexes = await db.collection(index.collection).listIndexes().maxTimeMS(1000).toArray();

      if (!indexes.find((x) => x.name === name)) {
        console.log(`Creating index ${name}`);
        await db.collection(index.collection).createIndex(index.fields, { name });
      }
    }
  }
}
