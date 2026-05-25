# 食物链小红书图文笔记生成器

> 基于 DeepSeek + wan2.7-image-pro 的 AI 驱动图文笔记生成系统，专为「食物链」猫粮品牌小红书内容运营设计。

---

## 🚀 快速启动

```bash
cd "/Users/choushuaiqi/Movies/Videos/Media.localized/Desktop/Github Manage/小红书图文笔记/版本管理/XP-FoodChain-copy"
python3 app.py
```

启动后在浏览器访问：**http://localhost:5188**

---

## 📋 功能说明

### 一、图文笔记生成

完整的 AI 二段式生成流程：

**第一步 · DeepSeek 骨架生成**
- 输入产品名称、核心卖点、目标受众、内容主题
- 调用 DeepSeek API 生成多页内容骨架（每页包含角色、标题、要点、场景描述）
- 骨架遵循小红书叙事结构：Hook → Truth → Solution → Science → CTA

**第二步 · wan2.7-image-pro 图片生成**
- 将骨架自动组装为 wan2.7-image-pro 专用 Prompt
- 支持 1 / 3 / 5 张可选（按需生成）
- 每张图分辨率：1024×1366（3:4 竖版，适配移动端）
- 生成完成后可一键打包 ZIP 下载

---

### 二、图片上传（参考图输入）

支持三类参考图上传，用于引导 AI 生成风格：

| 类型 | 说明 |
|------|------|
| 产品图 | 支持多图上传，多图时按页轮换使用 |
| 猫IP图 | 上传则注入画面；未上传则不使用 IP |
| 狗IP图 | 上传则注入画面；未上传则不使用 IP |

> **IP使用逻辑**：系统只在用户上传了IP素材时才将其注入生成 Prompt，不使用内置默认 IP，确保生成结果可控。

---

### 三、生成参数配置

| 参数 | 可选值 |
|------|--------|
| 产品名称 | 自由输入 |
| 核心卖点 | 自由输入 |
| 目标受众 | 自由输入 |
| 内容主题 | 0添加剂科普 / 天然食材 / A2绵羊乳 / 产品介绍 |
| 生成风格 | IP统一版 / 温馨质感版 / 现代冲击版 |
| 笔记张数 | 1 / 3 / 5 张 |
| 品牌色 | 默认 #3415c（自然绿） |
| 特殊需求 | 自定义补充说明 |

---

### 四、历史记录管理

- 每次生成后自动记录到 `history.json`
- 支持查看历史生成的图片
- 支持删除单条历史记录
- 历史记录按时间倒序展示

---

### 五、旧模式兼容（固定模板）

当未传入骨架数据时，系统自动回退到内置固定 Prompt 模板（按主题 × 页码匹配），保持向后兼容。

---

## 📁 文件结构

```
XP-FoodChain-copy/
├── app.py                          # Flask 后端主服务
├── templates/
│   └── index.html                  # 前端页面（单页应用）
├── requirements.txt                # Python 依赖
├── history.json                    # 生成历史记录
├── generated_user/                 # AI 生成图片输出目录（按 session 子目录存放）
├── uploads/                        # 用户上传的参考图片
├── IP形象/                          # 品牌 IP 素材（猫厨师教官 / 狗学员）
├── 双萃杯产品信息（含猫、犬）-20260408/  # 产品图素材
└── 示范案例/                        # 示范效果图
```

---

## ⚙️ 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3 + Flask + Flask-CORS |
| 前端 | HTML5 + CSS3 + Vanilla JS（单页应用） |
| 骨架生成 | DeepSeek Chat API（deepseek-chat） |
| 图片生成 | 阿里云百炼 wan2.7-image-pro |
| 图片传输 | Base64 多图输入（产品图 + IP图） |
| 打包下载 | Python zipfile（内存流，无临时文件） |

---

## 🔌 API 接口说明

| 接口 | 方法 | 说明 |
|------|------|------|
| `POST /api/upload` | POST | 上传参考图片（产品图 / IP猫 / IP狗） |
| `POST /api/generate-prompt` | POST | 调用 DeepSeek 生成内容骨架 |
| `POST /api/generate` | POST | 调用 wan2.7-image-pro 批量生成图片 |
| `GET /api/history` | GET | 获取历史生成记录 |
| `DELETE /api/history/<id>` | DELETE | 删除指定历史记录 |
| `GET /api/download/<session_id>` | GET | 打包下载指定 session 的所有图片 |
| `GET /output/<path>` | GET | 访问已生成图片 |
| `GET /uploads/<path>` | GET | 访问用户上传图片 |

---

## ❓ 常见问题

**Q: 启动后显示"连接失败"？**
A: 确保 `python3 app.py` 正在运行，刷新页面重试。

**Q: DeepSeek 骨架生成失败？**
A: 检查 `DEEPSEEK_API_KEY` 是否有效，或查看终端错误日志。

**Q: 图片生成失败？**
A: 检查 `API_KEY`（阿里云百炼）是否有效，或确认产品图路径存在。

**Q: 为什么有时生成的图片不带 IP 形象？**
A: 系统只在用户主动上传 IP 图时才使用。如需使用 IP，请在页面上传猫/狗 IP 素材。

**Q: 生成的图片存在哪里？**
A: 在 `generated_user/<session_id>/` 目录下，每次生成对应一个独立 session 子目录。
