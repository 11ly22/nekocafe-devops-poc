# NekoCafé

> NekoCafé 智慧餐饮预约平台 — 实验三 PoC 仓库

## 一键启动

```bash
make up   # 等价于 docker compose up -d --build
```

## 验证

```bash
curl http://localhost:8080/healthz
```


---

## 学生信息

- 班级：计23-2
- 学号：1234567
- 姓名：张三
- 生成日期：2026-05-30

## 本地快速启动

```bash
make up
curl http://localhost:8081/healthz
curl http://localhost:8082/healthz
```

Grafana: http://localhost:3000 （admin / nekocafe123）
