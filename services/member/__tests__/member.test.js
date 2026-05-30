const request = require('supertest');
const app = require('../src/index');

describe('Member Service', () => {
  test('GET /healthz returns ok', async () => {
    const res = await request(app).get('/healthz');
    expect(res.statusCode).toBe(200);
    expect(res.body.status).toBe('ok');
    expect(res.body.service).toBe('member');
  });

  test('GET /api/v1/members/:id returns member profile', async () => {
    const res = await request(app).get('/api/v1/members/demo-001');
    expect(res.statusCode).toBe(200);
    expect(res.body.member_id).toBe('demo-001');
    expect(res.body.level).toBeDefined();
  });

  test('POST /api/v1/members validates required fields', async () => {
    const res = await request(app).post('/api/v1/members').send({});
    expect(res.statusCode).toBe(400);
  });

  test('POST /api/v1/members creates member', async () => {
    const res = await request(app)
      .post('/api/v1/members')
      .send({ name: '测试用户', phone: '13800138000' });
    expect(res.statusCode).toBe(201);
    expect(res.body.member_id).toMatch(/^mem-/);
  });
});
