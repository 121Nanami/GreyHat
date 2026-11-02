# HTTP Echo Toy

Localhost echo server — prints and returns method, headers, and body as JSON.

## Run

```bash
node server.js
node server.js 9000
curl -X POST http://127.0.0.1:8765/hi -d 'hello'
```
