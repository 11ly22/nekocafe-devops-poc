// 会员服务 Express 入口
// NekoCafé Member Service v1.0.0

const express = require('express');
const pino = require('pino');
const { v4: uuidv4 } = require('uuid');

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  base: {
    service: 'member',
    version: '1.0.0',
    env: process.env.NODE_ENV || 'dev',
  },
});

const app = express();
const PORT = process.env.PORT || 8080;
const VERSION = '1.0.0';

app.use(express.json());

app.use((req, _res, next) => {
  req.traceId = req.headers['x-trace-id'] || uuidv4();
  logger.info({
    event: 'http.request',
    method: req.method,
    path: req.path,
    traceId: req.traceId,
  });
  next();
});

app.get('/healthz', (_req, res) => {
  res.json({ status: 'ok', service: 'member', version: VERSION });
});

function calcLevel(points) {
  if (points >= 10000) return 'gold';
  if (points >= 3000) return 'silver';
  return 'bronze';
}

app.get('/api/v1/members/:memberId', (req, res) => {
  const { memberId } = req.params;
  const points = 1500;
  res.json({
    member_id: memberId,
    name: '猫咪爱好者',
    level: calcLevel(points),
    points,
    join_date: '2025-01-01',
    trace_id: req.traceId,
  });
});

app.post('/api/v1/members', (req, res) => {
  const { name, phone } = req.body || {};
  if (!name || !phone) {
    return res.status(400).json({ error: 'name 和 phone 必填', trace_id: req.traceId });
  }
  logger.info({
    event: 'member.register',
    name,
    phone_masked: phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2'),
    trace_id: req.traceId,
  });
  const newMember = {
    member_id: `mem-${uuidv4().slice(0, 8)}`,
    name,
    level: 'bronze',
    points: 0,
    trace_id: req.traceId,
  };
  res.status(201).json(newMember);
});

app.post('/api/v1/members/:memberId/points', (req, res) => {
  const { memberId } = req.params;
  const { delta, reason } = req.body || {};
  if (!delta || delta <= 0) {
    return res.status(400).json({ error: 'delta 必须为正整数', trace_id: req.traceId });
  }
  logger.info({ event: 'points.add', memberId, delta, reason, trace_id: req.traceId });
  res.json({
    member_id: memberId,
    points_added: delta,
    new_total: 1500 + delta,
    new_level: calcLevel(1500 + delta),
    trace_id: req.traceId,
  });
});

app.use((err, _req, res, _next) => {
  logger.error({ event: 'unhandled_error', error: err.message });
  res.status(500).json({ error: 'Internal Server Error' });
});

if (require.main === module) {
  app.listen(PORT, () => {
    logger.info({ event: 'server.start', port: PORT });
  });
}

module.exports = app;
