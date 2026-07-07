# 乱写

随手丢入**语音、文字、图片**,AI 自动帮你循序渐进地建立知识库,并导出到 Obsidian。

- 每条乱写先进收件箱**原样存底**(原文/原音频/原图永久保留,任何 AI 结果可重放)
- AI 净化转写(只去语气词、纠错别字,**不改写不添意**),判断归属主题
- **高置信自动合并**进主题笔记(越写越厚,结构渐进重组);拿不准的进"待确认",你一键批准/改派/拒绝
- 每次合并有**版本快照 + diff + 一键回滚**;笔记末尾"记录轨迹"可溯源到每条原始碎片
- 主题笔记增量导出到 `OBVault/乱写/`(标准 Markdown + frontmatter + [[双链]],原子写入)

## 架构

```
iPhone (PWA, HTTPS)                     Mac (常驻服务)
┌─────────────────┐   Tailscale        ┌──────────────────────────────────────┐
│ 乱写/收件箱/待确认 │ ◄────HTTPS───────►│ FastAPI ──► SQLite (source of truth) │
│ 知识库/设置       │    REST + SSE     │   ├─ Worker(转写→归类→合并 状态机)     │
└─────────────────┘                    │   │   ├ mlx-whisper 本地转写(免费)    │
                                       │   │   ├ Haiku 净化+主题匹配            │
                                       │   │   └ Opus 内容合并重组              │
                                       │   └─ Exporter ──► OBVault/乱写/*.md  │
                                       └──────────────────────────────────────┘
```

## 快速开始

```bash
# 1. 配置 API key
cp .env.example .env   # 填入 ANTHROPIC_API_KEY

# 2. 启动(自动检测 Tailscale,有则 HTTPS,无则 HTTP)
./scripts/run.sh
```

前端已构建在 `web/dist`,由后端直接托管。改前端后重新构建:

```bash
cd web && npm install && npm run build
```

## 手机使用(HTTPS,录音必需)

1. Mac 和 iPhone 都安装 [Tailscale](https://tailscale.com) 并登录同一账号
2. `./scripts/run.sh` 会自动申请受信任证书并以 HTTPS 启动
3. iPhone Safari 打开 `https://<你的Mac名>.<tailnet>.ts.net:8787`
4. 分享 → 添加到主屏幕,即为原生般的 App

> 拍照和文字在 HTTP 下也能用;只有录音必须 HTTPS(浏览器 secure context 限制)。

## 开机常驻(可选)

```bash
cp scripts/com.luanxie.server.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.luanxie.server.plist
```

## 配置(.env)

| 变量 | 默认 | 说明 |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | 必填 |
| `AUTO_MERGE_CONFIDENCE` | `high` | 自动合并门槛:`high` 稳妥 / `medium` / `low` 全自动 |
| `CLASSIFY_MODEL` | `claude-haiku-4-5` | 净化+归类(便宜) |
| `MERGE_MODEL` | `claude-opus-4-8` | 合并重组(质量敏感) |
| `VAULT_EXPORT_DIR` | `OBVault/乱写` | Obsidian 导出目录 |
| `EXPORT_INTERVAL_MINUTES` | `0` | 定时导出间隔,0=仅手动 |

## 注意

- `OBVault/乱写/` 是**单向导出目标**,在里面手改的内容会被下次导出覆盖;要改笔记请在 App 里改(或改完别再导出该主题)
- 首次语音转写会自动下载 whisper 模型(约 1.6GB,之后常驻内存)
- 数据都在 `data/`:`luanxie.db`(SQLite)+ `media/`(原始音频图片)。备份这个目录即可
