const http = require('http');

const request = http.request(
  {
    host: 'localhost',
    port: '3000',
    timeout: 2000,
    path: '/ping',
  },
  (res) => {
    console.log(`STATUS: ${res.statusCode}`);
    if (res.statusCode == 200) {
      process.exit(0);
    } else {
      process.exit(1);
    }
  },
);

request.on('error', function (err) {
  console.log('ERROR');
  console.error(err);
  process.exit(1);
});

request.end();
