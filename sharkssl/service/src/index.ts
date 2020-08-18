import { createApp, tearDown } from './app';

async function main() {
  const app = await createApp();

  app.listen(3000, () => console.log('server started'));

  function exitHandler() {
    tearDown(app).then(() => process.exit());
  }

  process.on('exit', exitHandler);
  process.on('uncaughtException', exitHandler);
  process.on('SIGINT', exitHandler);
  process.on('SIGUSR1', exitHandler);
  process.on('SIGUSR2', exitHandler);
}

main().catch(console.error);
