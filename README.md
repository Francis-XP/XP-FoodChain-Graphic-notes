<div align="center">

# 🐾 XP-FoodChain 图文笔记生成器

**AI 驱动的小红书图文笔记一键生成工具**

输入产品信息，自动生成多页竖版图文笔记，支持预览编辑后一键出图

[![Python 3](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Web-green?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

</div>

---

## 🚀 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python3 app.py
```

启动后浏览器访问 **http://localhost:5188** 即可使用

---

## ✨ 功能一览

### 📝 图文笔记生成
填写产品信息后，两步完成生成：

1. **AI 生成骨架** — 自动生成每页的标题、信息要点、画面描述，内置叙事结构（封面吸引 → 误区揭示 → 解决方案 → 科学背书 → 行动号召）
2. **预览 & 编辑** — 在页面中直接修改骨架内容，确认满意后再出图
3. **AI 出图** — 根据骨架批量生成图片，支持 1 / 3 / 5 张按需选择，竖版 3:4 适配移动端

### 🎛️ 可配置项

| 配置项 | 说明 |
|:---|------|
| 产品名称 | 必填，自由输入 |
| 核心卖点 | 逗号或换行分隔，AI 据此生成每页内容 |
| 目标受众 | 自由输入，默认"养猫宠主" |
| 内容主题 | 自由输入，如：误区科普、成分解析、产品介绍等 |
| 图文张数 | 1 / 3 / 5 张可选 |
| 风格描述 | 自由输入，如：温馨自然、现代简约、高级质感等 |
| 品牌色 | 颜色选择器，默认自然绿 |
| 特殊要求 | 自由输入补充说明 |

### 🖼️ 参考图上传
支持三类参考图上传，用于引导 AI 生成风格：

| 类型 | 说明 |
|:---:|------|
| 产品图 | 支持多图上传，多图时按页轮换使用 |
| 猫IP图 | 上传则注入画面；未上传则不使用 IP |
| 狗IP图 | 上传则注入画面；未上传则不使用 IP |

> **IP使用逻辑**：系统只在用户上传了IP素材时才将其注入生成 Prompt，不使用内置默认 IP，确保生成结果可控。

### 📦 历史记录管理
- 每次生成后自动记录到 `history.json`
- 支持查看历史生成的图片
- 支持删除单条历史记录
- 历史记录按时间倒序展示

### 📥 一键下载
- 打包下载生成的全部图片为 ZIP

---

## ⚙️ 技术栈

<p>
  <img src="https://img.shields.io/badge/Python-3-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-Backend-green?logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/HTML5-Frontend-orange?logo=html5&logoColor=white" />
  <img src="https://img.shields.io/badge/CSS3-Styling-blueviolet?logo=css3&logoColor=white" />
  <img src="https://img.shields.io/badge/JavaScript-Interactive-yellow?logo=javascript&logoColor=black" />
</p>

---

<div align="center">

**Made with ❤️ for 食物链**

</div>
