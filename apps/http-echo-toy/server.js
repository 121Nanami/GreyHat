#!/usr/bin/env node
/** Tiny HTTP echo server for local debugging. */
const http = require("http");
const port = Number(process.env.PORT || process.argv[2] || 8765);

const server = http.createServer(async (req, res) => {
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const body = Buffer.concat(chunks).toString("utf8");
  const out = {
    method: req.method,
    url: req.url,
    httpVersion: req.httpVersion,
    headers: req.headers,
    body,
    at: new Date().toISOString(),
  };
  const pretty = JSON.stringify(out, null, 2);
  console.log("—".repeat(40));
  console.log(pretty);
  res.writeHead(200, { "content-type": "application/json; charset=utf-8" });
  res.end(pretty + "\n");
});

server.listen(port, "127.0.0.1", () => {
  console.log(`http-echo-toy listening on http://127.0.0.1:${port}`);
});
