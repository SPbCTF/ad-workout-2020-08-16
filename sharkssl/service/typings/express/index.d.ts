import type { MongoClient, Db } from 'mongodb';

declare global {
  namespace Express {
    interface Application {
      db: Db;
      mongo: MongoClient;
    }
    interface Request {
      username?: string;
    }
  }
}
