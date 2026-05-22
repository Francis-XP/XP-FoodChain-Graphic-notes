#!/usr/bin/env python3
"""
食物链小红书图文笔记生成器 - Flask后端服务
真正可运行的图文笔记生成系统
"""

import os
import base64
import json
import time
import random
import string
import zipfile
import io
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)
CORS(app)

# ============== 配置 ==============
API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
API_KEY = "sk-290bbc05105342ecbe6db00eb050b080"

# DeepSeek API 配置（用于生成 Prompt 骨架）
DEEPSEEK_API_KEY = "sk-a57ebeba6a1347358b3eebf69c56c6e6"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

BASE_DIR = "/Users/choushuaiqi/Movies/Videos/Media.localized/Desktop/食物链-图文笔记"
OUTPUT_DIR = os.path.join(BASE_DIR, "generated_user")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 产品图片路径
PRODUCT_DIR = "/Users/choushuaiqi/Movies/Videos/Media.localized/Desktop/食物链-图文笔记/双萃杯产品信息（含猫、犬）-20260408"
IP_DIR = "/Users/choushuaiqi/Movies/Videos/Media.localized/Desktop/食物链-图文笔记/IP形象"

# ============== 工具函数 ==============
def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_image_base64(path):
    """读取图片并转为base64"""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def download_image(url, output_path):
    """下载图片到本地"""
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"下载失败: {e}")
    return False

def generate_session_id():
    """生成会话ID"""
    return f"session_{int(time.time())}_{''.join(random.choices(string.ascii_lowercase, k=6))}"

# ============== DeepSeek 骨架生成 ==============
DEEPSEEK_SYSTEM_PROMPT = """你是一个专业的小红书内容策划专家。请根据用户提供的产品信息，生成小红书图文笔记的框架。

要求：
1. 共N页（由用户指定），每页有明确的信息递进逻辑
2. 第1页必须是hook（制造冲突/痛点，吸引点击，标题要有冲击力）
3. 最后一页必须是CTA（行动号召，引导购买或关注）
4. 中间页依次为：truth（揭露真相/误区）→ solution（给出解决方案）→ science（科学背书/成分解析）

每页包含：
- role: 该页角色（hook / truth / solution / science / cta）
- title: 中文标题（吸引人，适合小红书风格）
- points: 中文信息要点数组（1-3条，简洁有力）
- scene: 英文画面描述（用于AI生图，包含布局、配色、氛围、风格）

输出格式：严格JSON数组，不要输出```json或任何其他文字，只输出纯JSON。
"""

def call_deepseek_for_skeleton(product_name, selling_points, target_audience, theme, page_count, style_desc, brand_color):
    """调用 DeepSeek API 生成 Prompt 骨架"""
    system_prompt = """你是一个专业的小红书内容策划专家。请根据用户提供的产品信息，生成小红书图文笔记的框架。

要求：
1. 共N页（由用户指定），每页有明确的信息递进逻辑
2. 第1页必须是hook（制造冲突/痛点，吸引点击，标题要有冲击力）
3. 最后一页必须是CTA（行动号召，引导购买或关注）
4. 中间页依次为：truth（揭露真相/误区）→ solution（给出解决方案）→ science（科学背书/成分解析）

每页包含：
- role: 该页角色（hook / truth / solution / science / cta）
- title: 中文标题（吸引人，适合小红书风格）
- points: 中文信息要点数组（1-3条，简洁有力）
- scene: 英文画面描述（用于AI生图，包含布局、配色、氛围、风格）

输出格式：严格JSON数组，不要输出```json或任何其他文字，只输出纯JSON。"""

    try:
        user_prompt = f"""产品信息：
- 产品名称：{product_name}
- 核心卖点：{selling_points}
- 目标受众：{target_audience}
- 内容主题：{theme}
- 笔记张数：{page_count}张
- 生成风格：{style_desc}
- 品牌色：{brand_color}

请为这个产品生成 {page_count} 张小红书图文笔记的内容框架。每张图对应一页，要有清晰的信息递进逻辑。"""

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }

        print(f"调用 DeepSeek API 生成骨架...")
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
        result = response.json()

        if response.status_code == 200:
            content = result["choices"][0]["message"]["content"]
            # 尝试解析 JSON（可能有包裹）
            try:
                skeleton = json.loads(content)
                # 统一格式：如果是 {"skeleton": [...]} 则提取
                if "skeleton" in skeleton:
                    skeleton = skeleton["skeleton"]
                if not isinstance(skeleton, list):
                    raise ValueError("返回格式不是数组")
                return {"success": True, "skeleton": skeleton}
            except Exception as je:
                print(f"JSON解析失败: {je}, 原始返回: {content[:200]}")
                return {"success": False, "error": f"JSON解析失败: {str(je)}"}
        else:
            error_msg = result.get("message", str(result))
            print(f"DeepSeek API 错误: {error_msg}")
            return {"success": False, "error": error_msg}

    except Exception as e:
        print(f"DeepSeek 调用异常: {e}")
        return {"success": False, "error": str(e)}

def build_prompt_from_skeleton(skeleton_item, style_desc, color_scheme, product_desc, ip_desc):
    """将骨架条目转换为 wan2.7-image-pro 的 Prompt"""
    role = skeleton_item.get("role", "")
    title = skeleton_item.get("title", "")
    points = skeleton_item.get("points", [])
    scene = skeleton_item.get("scene", "")

    # 将中文要点格式化为英文 info-cards
    points_en = f"Info-cards: " + ", ".join([f'"{p}"' for p in points]) if points else ""

    prompt = f"""Create a Xiaohongshu infographic image. {ip_desc}
Title: "{title}"
{points_en}
{scene}
{style_desc}
{color_scheme}
{product_desc}
High information density, vertical 3:4, mobile-first design."""

    return prompt

# ============== 提示词模板 ==============
PROMPT_TEMPLATES = {
    "0_additive": {
        "page1": """Create a Xiaohongshu educational infographic. {ip_description}. Large Chinese title: "你买的『0添加剂』猫罐头，可能骗了你！" {style_description}. Info-cards: "❌ 『0添加』≠『0添加剂』" "❌ 无诱食剂≠无全部添加" "❌ 人工矿物质预混料仍在". {product_description}. Product on podium with spotlight. {color_scheme}. High information density. Vertical 3:4.""",
        "page2": """Create a Xiaohongshu expose infographic. {ip_description}. Title: "行业0添加的真相". {style_description}. Info-panel: "矿物质预混料 ✗" "人工合成维生素 ✗" "人工牛磺酸 ✗". {product_description} with checkmark "真正0添加认证". {color_scheme}. High information density. Vertical 3:4.""",
        "page3": """Create a Xiaohongshu product solution infographic. {ip_description}. Title: "食物链双萃杯 · 天然食材替代方案". {style_description}. Cards: "天然鸡肉→安全矿物质" "天然兔肉→完整氨基酸" "A2绵羊乳→天然营养". {product_description} with golden seal. {color_scheme}. High information density. Vertical 3:4.""",
        "page4": """Create a Xiaohongshu science education infographic. {ip_description}. Title: "A2型绵羊乳 · 双重健康升级". {style_description}. Health badges: "🛡️ 肠道亲和力UP" "💪 蛋白质吸收率UP" "🌟 低敏配方". {product_description} with A2 milk drop. {color_scheme}. High information density. Vertical 3:4.""",
        "page5": """Create a Xiaohongshu call-to-action. {ip_description}. Title: "选择真正的0添加 · 一餐一杯刚刚好". {style_description}. Stats: "✅ 0人工添加剂 | ✅ 5种天然食材 | ✅ 全价营养". {product_description} on wooden table with herbs. {color_scheme}. Vertical 3:4."""
    },
    "natural_ingredients": {
        "page1": """Create a Xiaohongshu product showcase. {ip_description}. Title: "天然食材的力量" {style_description}. Natural ingredient icons floating. {product_description}. {color_scheme}. High information density. Vertical 3:4.""",
        "page2": """Create a Xiaohongshu comparison infographic. {ip_description}. Title: "天然 vs 人工添加剂". {style_description}. Two-column comparison. {product_description}. {color_scheme}. Vertical 3:4.""",
        "page3": """Create a Xiaohongshu ingredients breakdown. {ip_description}. Title: "配料表里有什么". {style_description}. Ingredient cards with icons. {product_description}. {color_scheme}. Vertical 3:4.""",
        "page4": """Create a Xiaohongshu health benefits. {ip_description}. Title: "天然食材的健康益处". {style_description}. Health icons and benefits. {product_description}. {color_scheme}. Vertical 3:4.""",
        "page5": """Create a Xiaohongshu CTA. {ip_description}. Title: "选择天然 选择健康". {style_description}. {product_description}. {color_scheme}. Vertical 3:4."""
    },
    "a2_milk": {
        "page1": """Create a Xiaohongshu education page. {ip_description}. Title: "认识A2型绵羊乳". {style_description}. A2 milk drop graphic. {product_description}. {color_scheme}. Vertical 3:4.""",
        "page2": """Create a Xiaohongshu science page. {ip_description}. Title: "A2蛋白 vs 普通蛋白". {style_description}. Comparison diagram. {product_description}. {color_scheme}. Vertical 3:4.""",
        "page3": """Create a Xiaohongshu benefits page. {ip_description}. Title: "A2绵羊乳的三大好处". {style_description}. Benefit cards. {product_description}. {color_scheme}. Vertical 3:4.""",
        "page4": """Create a Xiaohongshu data page. {ip_description}. Title: "数据说话". {style_description}. Statistics and charts. {product_description}. {color_scheme}. Vertical 3:4.""",
        "page5": """Create a Xiaohongshu recommendation. {ip_description}. Title: "为什么选择A2配方". {style_description}. {product_description}. {color_scheme}. Vertical 3:4."""
    },
    "product_intro": {
        "page1": """Create a Xiaohongshu hero image. {ip_description}. Title: "食物链双萃杯". {style_description}. Product showcase. {product_description}. {color_scheme}. Vertical 3:4.""",
        "page2": """Create a Xiaohongshu features. {ip_description}. Title: "产品特点". {style_description}. Feature cards. {product_description}. {color_scheme}. Vertical 3:4.""",
        "page3": """Create a Xiaohongshu ingredients. {ip_description}. Title: "成分解析". {style_description}. Ingredient breakdown. {product_description}. {color_scheme}. Vertical 3:4.""",
        "page4": """Create a Xiaohongshu usage. {ip_description}. Title: "使用方法". {style_description}. Usage guide. {product_description}. {color_scheme}. Vertical 3:4.""",
        "page5": """Create a Xiaohongshu purchase. {ip_description}. Title: "立即购买". {style_description}. CTA and product. {product_description}. {color_scheme}. Vertical 3:4."""
    }
}

# 风格描述
STYLE_DESCRIPTIONS = {
    "ip_version": "Cat teacher with chef hat and green apron, dog student with chef hat. Classroom style.",
    "beautiful_A": "Warm tones, wooden podium, soft natural lighting, elegant cream and gold accents.",
    "beautiful_B": "Modern dark background, neon green accents, holographic effects, bold typography."
}

COLOR_SCHEMES = {
    "ip_version": "Natural green brand color #3415c, white background.",
    "beautiful_A": "Warm cream, gold, and soft mint green. Luxurious feel.",
    "beautiful_B": "Dark charcoal with vibrant mint green neon. High contrast."
}

IP_DESCRIPTIONS = {
    "ip_version": "The provided CAT CHARACTER wearing chef hat and green apron. The provided DOG CHARACTER wearing chef hat and green apron.",
    "beautiful_A": "Cute cartoon cat character with chef hat and green apron. Cute cartoon dog character with chef hat.",
    "beautiful_B": "Stylized cat character with chef hat in modern illustration. Stylized dog character with chef hat."
}

# ============== 路由 ==============
@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

# ============== 文件上传 ==============
@app.route('/api/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    try:
        upload_type = request.form.get('type', 'product')  # product | ip_cat | ip_dog

        # 处理多文件上传（产品图）
        if 'files' in request.files:
            files = request.files.getlist('files')
            uploaded_files = []

            for file in files:
                if file.filename == '':
                    continue
                if file and allowed_file(file.filename):
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"{upload_type}_{int(time.time())}_{random.randint(1000, 9999)}.{ext}"
                    filepath = os.path.join(UPLOAD_DIR, filename)
                    file.save(filepath)
                    uploaded_files.append({
                        "filename": filename,
                        "url": f"/uploads/{filename}"
                    })

            if uploaded_files:
                return jsonify({
                    "success": True,
                    "files": uploaded_files,
                    "message": f"成功上传 {len(uploaded_files)} 个文件"
                })
            return jsonify({"success": False, "error": "没有上传有效的文件"}), 400

        # 单文件上传
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "没有文件"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"success": False, "error": "文件名为空"}), 400

        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{upload_type}_{int(time.time())}_{random.randint(1000, 9999)}.{ext}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            file.save(filepath)

            return jsonify({
                "success": True,
                "filename": filename,
                "url": f"/uploads/{filename}",
                "message": "上传成功"
            })

        return jsonify({"success": False, "error": "不支持的文件类型"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    """提供上传的图片"""
    return send_from_directory(UPLOAD_DIR, filename)

# ============== Prompt 骨架生成 ==============
@app.route('/api/generate-prompt', methods=['POST'])
def generate_prompt():
    """调用 DeepSeek 生成 Prompt 骨架"""
    try:
        data = request.get_json()
        product_name = data.get('productName', '')
        selling_points = data.get('sellingPoints', '')
        target_audience = data.get('targetAudience', '')
        theme = data.get('theme', '')
        page_count = int(data.get('pageCount', 5))
        style_desc = data.get('styleDesc', '温馨自然')
        brand_color = data.get('brandColor', '#3415c')

        print(f"DeepSeek 骨架生成请求: 产品={product_name}, 张数={page_count}")

        result = call_deepseek_for_skeleton(product_name, selling_points, target_audience, theme, page_count, style_desc, brand_color)

        if result["success"]:
            return jsonify({
                "success": True,
                "skeleton": result["skeleton"]
            })
        else:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 500

    except Exception as e:
        print(f"骨架生成失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ============== 图片生成（兼容骨架模式 + 旧模板模式） ==============
@app.route('/api/generate', methods=['POST'])
def generate():
    """生成图文笔记"""
    try:
        data = request.get_json()

        product_name = data.get('productName', '未命名产品')
        product_image = data.get('productImage', '')  # 用户上传的产品图文件名
        ip_cat_image = data.get('ipCatImage', '')     # 用户上传的猫IP图
        ip_dog_image = data.get('ipDogImage', '')     # 用户上传的狗IP图
        page_count = data.get('pageCount', 5)        # 图文笔记张数
        theme = data.get('theme', '0_additive')
        style = data.get('style', 'ip_version')
        special_req = data.get('specialReqs', '')
        # 新模式：使用 DeepSeek 生成的骨架
        skeleton = data.get('skeleton', None)  # list of skeleton items

        print(f"收到生成请求: 产品={product_name}, 张数={page_count}, 主题={theme}, 风格={style}")
        print(f"自定义图片: 产品图={product_image}, 猫IP={ip_cat_image}, 狗IP={ip_dog_image}")

        # 创建会话目录
        session_id = generate_session_id()
        session_dir = os.path.join(OUTPUT_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)

        # 加载参考图片 - 优先使用用户上传的，否则使用默认
        # 处理产品图片（支持多图）
        product_images = []
        if product_image:
            # 支持多图，格式：image1.png,image2.png,image3.png
            image_list = product_image.split(',')
            for img in image_list:
                img = img.strip()
                if img and os.path.exists(os.path.join(UPLOAD_DIR, img)):
                    product_images.append(os.path.join(UPLOAD_DIR, img))
                    print(f"使用用户上传的产品图: {img}")

        # 如果没有上传产品图，使用默认
        if not product_images:
            default_path = f"{PRODUCT_DIR}/双萃杯-猫用/餐盒白底图/鸡肉兔肉-餐盒正视图.png"
            if not os.path.exists(default_path):
                default_path = f"{PRODUCT_DIR}/双萃杯-猫用/餐盒白底图/鸡肉兔肉-餐盒正视图.png"
            product_images.append(default_path)

        # 处理IP图片 - 用户上传了就用新的，没上传就不用IP（禁用默认IP）
        ip_cat_path = None
        ip_dog_path = None

        if ip_cat_image and os.path.exists(os.path.join(UPLOAD_DIR, ip_cat_image)):
            ip_cat_path = os.path.join(UPLOAD_DIR, ip_cat_image)
            print(f"使用用户上传的猫IP图: {ip_cat_path}")

        if ip_dog_image and os.path.exists(os.path.join(UPLOAD_DIR, ip_dog_image)):
            ip_dog_path = os.path.join(UPLOAD_DIR, ip_dog_image)
            print(f"使用用户上传的狗IP图: {ip_dog_path}")

        product_img = load_image_base64(product_images[0])
        cat_ip = load_image_base64(ip_cat_path) if ip_cat_path else None
        dog_ip = load_image_base64(ip_dog_path) if ip_dog_path else None

        # 获取提示词模板（旧模式备用）
        theme_templates = PROMPT_TEMPLATES.get(theme, PROMPT_TEMPLATES["0_additive"])
        style_desc = STYLE_DESCRIPTIONS.get(style, STYLE_DESCRIPTIONS["ip_version"])
        color_scheme = COLOR_SCHEMES.get(style, COLOR_SCHEMES["ip_version"])

        # 根据实际上传情况构建IP描述
        if ip_cat_path and ip_dog_path:
            ip_desc = "The provided character images."
        elif ip_cat_path:
            ip_desc = "The provided character image."
        elif ip_dog_path:
            ip_desc = "The provided character image."
        else:
            ip_desc = ""

        # 构建产品描述
        product_desc = f"Product: {product_name}."
        if special_req:
            product_desc += f" Special requirements: {special_req}"

        generated_images = []

        # 生成指定数量的图片
        for page_num in range(1, page_count + 1):
            page_key = f"page{page_num}"
            if page_key not in theme_templates:
                continue

            # 多图轮换使用
            product_img = load_image_base64(product_images[(page_num - 1) % len(product_images)])

            # ========== 新模式：使用骨架构建 Prompt ==========
            if skeleton and page_num <= len(skeleton):
                sk = skeleton[page_num - 1]
                prompt = build_prompt_from_skeleton(sk, style_desc, color_scheme, product_desc, ip_desc)
                print(f"使用骨架生成第{page_num}页: {sk.get('title', '')}")
            # ========== 旧模式：使用固定模板 ==========
            else:
                prompt_template = theme_templates[page_key]
                prompt = prompt_template.format(
                    ip_description=ip_desc,
                    style_description=style_desc,
                    color_scheme=color_scheme,
                    product_description=product_desc
                )

            print(f"生成第{page_num}页...")

            # 构建消息内容 - 只包含实际上传的图片
            message_content = [
                {"type": "image", "image": f"data:image/png;base64,{product_img}"},
                {"type": "text", "text": prompt}
            ]

            # 如果用户上传了IP图片才添加
            if cat_ip:
                message_content.insert(1, {"type": "image", "image": f"data:image/png;base64,{cat_ip}"})
            if dog_ip:
                message_content.insert(2, {"type": "image", "image": f"data:image/png;base64,{dog_ip}"})

            # 调用API
            payload = {
                "model": "wan2.7-image-pro",
                "input": {
                    "messages": [{
                        "role": "user",
                        "content": message_content
                    }]
                },
                "parameters": {"size": "1024*1366", "n": 1, "watermark": False}
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            }

            try:
                response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
                result = response.json()

                if response.status_code == 200:
                    choices = result.get("output", {}).get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", [])
                        for item in content:
                            if item.get("type") == "image":
                                img_url = item.get("image", "")
                                if img_url.startswith("http"):
                                    output_file = f"page_{page_num}.png"
                                    output_path = os.path.join(session_dir, output_file)
                                    if download_image(img_url, output_path):
                                        generated_images.append({
                                            "page": page_num,
                                            "file": f"{session_id}/{output_file}",
                                            "url": f"/output/{session_id}/{output_file}"
                                        })
                                        print(f"第{page_num}页保存成功")
                                    else:
                                        print(f"第{page_num}页下载失败")
                                break
                else:
                    print(f"API错误: {response.status_code} - {result}")

            except Exception as e:
                print(f"第{page_num}页生成异常: {e}")

            time.sleep(2)

        # 保存历史记录
        theme_names = {
            "0_additive": "0添加剂认知误区科普",
            "natural_ingredients": "天然食材替代方案",
            "a2_milk": "A2绵羊乳健康科普",
            "product_intro": "产品介绍"
        }
        style_names = {
            "ip_version": "IP统一版",
            "beautiful_A": "温馨质感版",
            "beautiful_B": "现代冲击版"
        }
        page_count_names = {
            1: "1张",
            3: "3张",
            5: "5张"
        }

        history_record = {
            "id": session_id,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "product_name": product_name,
            "product_image": product_image,
            "ip_cat_image": ip_cat_image,
            "ip_dog_image": ip_dog_image,
            "page_count": page_count,
            "page_count_name": page_count_names.get(page_count, f"{page_count}张"),
            "theme": theme,
            "theme_name": theme_names.get(theme, theme),
            "style": style,
            "style_name": style_names.get(style, style),
            "special_req": special_req,
            "images": generated_images,
            "session_id": session_id
        }

        history = load_history()
        history.append(history_record)
        save_history(history)

        return jsonify({
            "success": True,
            "session_id": session_id,
            "images": generated_images,
            "message": f"成功生成 {len(generated_images)}/{page_count} 张图片"
        })

    except Exception as e:
        print(f"生成失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/output/<path:filename>')
def serve_output(filename):
    """提供生成结果的图片"""
    return send_from_directory(OUTPUT_DIR, filename)

@app.route('/gallery/<version>')
def gallery(version):
    """获取指定版本的图片列表"""
    version_dirs = {
        "ip_version": "generated_ip_version",
        "beautiful_A": "generated_beautiful_A",
        "beautiful_B": "generated_beautiful_B"
    }

    dir_name = version_dirs.get(version)
    if not dir_name:
        return jsonify({"error": "Invalid version"}), 400

    base = os.path.join(BASE_DIR, dir_name)
    if not os.path.exists(base):
        return jsonify({"images": []})

    images = []
    for f in sorted(os.listdir(base)):
        if f.endswith('.png'):
            images.append({
                "file": f,
                "url": f"/gallery-files/{dir_name}/{f}"
            })

    return jsonify({"images": images})

@app.route('/gallery-files/<path:filename>')
def serve_gallery(filename):
    """提供图库图片"""
    return send_from_directory(BASE_DIR, filename)

# ============== 历史记录 ==============
def load_history():
    """加载历史记录"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    """保存历史记录"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存历史失败: {e}")
        return False

@app.route('/api/history', methods=['GET'])
def get_history():
    """获取历史记录"""
    history = load_history()
    # 按时间倒序
    history.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify({
        "success": True,
        "history": history,
        "total": len(history)
    })

@app.route('/api/history', methods=['POST'])
def add_history():
    """添加历史记录"""
    try:
        data = request.get_json()
        record = {
            "id": data.get('id', ''),
            "created_at": data.get('created_at', time.strftime('%Y-%m-%d %H:%M:%S')),
            "product_name": data.get('product_name', ''),
            "flavor": data.get('flavor', ''),
            "flavor_name": data.get('flavor_name', ''),
            "theme": data.get('theme', ''),
            "theme_name": data.get('theme_name', ''),
            "style": data.get('style', ''),
            "style_name": data.get('style_name', ''),
            "special_req": data.get('special_req', ''),
            "images": data.get('images', []),
            "session_id": data.get('session_id', '')
        }

        history = load_history()
        history.append(record)
        save_history(history)

        return jsonify({"success": True, "message": "记录已保存"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history/<record_id>', methods=['DELETE'])
def delete_history(record_id):
    """删除历史记录"""
    try:
        history = load_history()
        new_history = [r for r in history if r.get('id') != record_id]
        save_history(new_history)
        return jsonify({"success": True, "message": "记录已删除"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/history-files/<path:filename>')
def serve_history_files(filename):
    """提供历史记录图片"""
    return send_from_directory(OUTPUT_DIR, filename)

# ============== 下载功能 ==============
@app.route('/api/download/<session_id>', methods=['GET'])
def download_images(session_id):
    """打包下载指定session的所有图片"""
    try:
        session_dir = os.path.join(OUTPUT_DIR, session_id)
        if not os.path.exists(session_dir):
            return jsonify({"success": False, "error": "目录不存在"}), 404

        # 获取该session下所有PNG图片
        images = [f for f in os.listdir(session_dir) if f.endswith('.png')]
        if not images:
            return jsonify({"success": False, "error": "没有图片文件"}), 404

        # 按页码排序
        images.sort(key=lambda x: int(x.replace('page_', '').replace('.png', '')))

        # 创建ZIP文件
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for img_name in images:
                img_path = os.path.join(session_dir, img_name)
                with open(img_path, 'rb') as f:
                    zf.writestr(img_name, f.read())

        memory_file.seek(0)

        # 生成文件名
        zip_name = f"图文笔记_{session_id}.zip"

        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_name
        )
    except Exception as e:
        print(f"下载失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ============== 启动 ==============
if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════╗
║     食物链小红书图文笔记生成器                            ║
║     使用 AI模型 生成                                     ║
║     访问地址: http://localhost:5188                       ║
╚══════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5188, debug=True)
