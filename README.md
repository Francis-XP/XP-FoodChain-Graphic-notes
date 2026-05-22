# 食物链小红书图文笔记生成器

## 🚀 快速启动

### 方式一：一键启动（推荐）

```bash
cd "/Users/choushuaiqi/Movies/Videos/Media.localized/Desktop/食物链-图文笔记"
python3 app.py
```

然后在浏览器打开：**http://localhost:5188**

### 方式二：直接预览HTML（仅查看效果）

打开文件：`图文笔记生成器.html`

> 注意：此方式只能查看已生成的图片，无法调用AI生成新内容

---

## 📋 功能说明

### 效果预览页
- 查看3个版本的图文笔记：IP统一版 / 温馨质感版 / 现代冲击版
- 点击卡片放大预览，支持键盘翻页

### 生成新内容页
- **产品名称**：输入产品名
- **产品配方**：鸡肉兔肉 / 鸡肉南瓜 / 鸡肉鸽肉
- **内容主题**：0添加剂科普 / 天然食材 / A2绵羊乳 / 产品介绍
- **生成风格**：IP统一版 / 温馨质感版 / 现代冲击版
- **特殊需求**：自定义补充说明

---

## 📁 文件结构

```
食物链-图文笔记/
├── app.py              # Flask后端服务（处理API调用）
├── templates/
│   └── index.html      # 前端页面模板
├── requirements.txt    # Python依赖
├── generated_user/     # 用户生成的内容存放目录
├── generated_ip_version/    # IP统一版效果
├── generated_beautiful_A/   # 温馨质感版效果
└── generated_beautiful_B/   # 现代冲击版效果
```

---

## ⚙️ 技术栈

- **后端**：Python Flask
- **前端**：HTML5 + CSS3 + JavaScript
- **AI模型**：wan2.7-image-pro

---

## ❓ 常见问题

**Q: 启动后显示"连接失败"？**
A: 确保 `python3 app.py` 正在运行，刷新页面重试。

**Q: 生成失败怎么办？**
A: 检查API Key是否有效，或查看终端错误日志。

**Q: 图片没有生成？**
A: 检查产品图片路径是否存在，或手动指定产品图路径。
