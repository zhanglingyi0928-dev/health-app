const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const DIR = __dirname;

// ─── 静态文件 MIME ────────────────────────────────────────────────
const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.js':   'application/javascript',
  '.css':  'text/css',
  '.json': 'application/json',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.gif':  'image/gif',
  '.svg':  'image/svg+xml',
  '.ico':  'image/x-icon',
};

// ─── AI 代理配置 ──────────────────────────────────────────────────
const AI_TARGET_HOST = 'tc-paperhub.diezhi.net';
const AI_TARGET_PATH = '/v1/chat/completions';
const AI_API_KEY = 'sk-GAY-dlys5gibHWJReSrw6DOdmNthxVAQyGxpb8DLDYXB9ZEQ';

const server = http.createServer((req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // ─── AI API 代理 ──────────────────────────────────────────────
  if (req.url === '/v1/chat/completions' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      const options = {
        hostname: AI_TARGET_HOST,
        path: AI_TARGET_PATH,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + AI_API_KEY,
        }
      };

      const proxyReq = https.request(options, (proxyRes) => {
        res.writeHead(proxyRes.statusCode, proxyRes.headers);
        proxyRes.pipe(res);
      });

      proxyReq.on('error', (err) => {
        res.writeHead(502);
        res.end('Proxy error: ' + err.message);
      });

      proxyReq.write(body);
      proxyReq.end();
    });
    return;
  }

  // ─── 静态文件服务 ──────────────────────────────────────────────
  let filePath = path.join(DIR, req.url === '/' ? 'health-app.html' : req.url);
  const ext = path.extname(filePath).toLowerCase();
  const contentType = mimeTypes[ext] || 'text/plain';

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Not Found');
      return;
    }
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log('═══════════════════════════════════════');
  console.log('  🏃 健康打卡 App 已启动');
  console.log(`  📍 http://localhost:${PORT}`);
  console.log('  🔗 AI 对话已就绪');
  console.log('  ⏹  关闭此窗口即可停止服务');
  console.log('═══════════════════════════════════════');
});
