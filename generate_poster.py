#!/usr/bin/env python3
"""
AI 概念海报生成工程脚本
========================
作品：《文明代码：从甲骨到AI》 & 《和融世界·文脉生根》
比赛：AI 创作大赛
环境：Python 3.10+

依赖安装：
    pip install openai pillow requests

使用方式：
    python generate_poster.py --work 1        # 生成作品一
    python generate_poster.py --work 2        # 生成作品二
    python generate_poster.py --work all      # 生成全部
    python generate_poster.py --work 1 --upscale 4x  # 生成并放大
"""

import os
import json
import argparse
import time
from datetime import datetime
from typing import Optional

# ── 配置 ──────────────────────────────────────────────
CONFIG = {
    # API 配置（请替换为实际 API Key 和 endpoint）
    "api_key": os.environ.get("AI_API_KEY", "YOUR_API_KEY_HERE"),
    "api_base": os.environ.get("AI_API_BASE", "https://api.openai.com/v1"),
    "model": "dall-e-3",                  # 或 stability-ai/stable-diffusion-3

    # 输出配置
    "output_dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs"),
    "save_metadata": True,                 # 每次生成自动保存参数元数据

    # 放大配置
    "upscale_enabled": True,
    "upscale_method": "esrgan",            # esrgan / real-esrgan
}

# ── Prompt 模板库 ─────────────────────────────────────

PROMPTS = {
    "work_1": {
        "title": "文明代码：从甲骨到AI",
        "title_en": "The Civilization Code: From Oracle to AI",
        "positive": (
            "大师级概念海报设计，纵向竖构图，垂直比例约3:4，"
            "一棵巨大的文明之树贯穿天地。"
            "树根深埋于中华文明土壤之中，根系由甲骨文、金文、篆书、竹简、古籍纹样组成，"
            "散发古老金色光芒。"
            "文字逐渐演化，树根向上延伸时自然转化为二进制代码0和1，"
            "再转化为发光的数据流与神经网络结构。"
            "树干融合水墨肌理、青铜器纹样、祥云纹饰与未来科技电路纹理，"
            "远看是树皮，近看隐约呈现长城轮廓。"
            "树冠由无数AI神经节点、数字光点和发光网络组成，向全球延展。"
            "顶部悬浮发光地球，连接世界各大洲。"
            "树冠中隐藏多国语言'你好'，包括Hello、Bonjour、Hola、こんにちは、مرحباً。"
            "金色与深蓝色主色调，东方美学与未来科技融合，"
            "超精细细节，史诗级视觉冲击，电影级灯光，8K超高分辨率，"
            "全球传播主题，文明传承与科技创新，国际设计大奖风格"
        ),
        "negative": (
            "文字模糊，元素堆砌杂乱，色彩失衡，低分辨率，"
            "模糊不清，变形扭曲，过度曝光，暗部细节丢失，"
            "构图倾斜，西方中心视角，文化符号滥用，不协调"
        ),
        "style": "东方美学 × 赛博未来 (Cyber-Orientalism)",
        "aspect_ratio": "3:4",
        "seed_recommendations": [42, 128, 256, 512, 1024],
        "cfg_scale": 7.5,
        "steps": 30,
    },
    "work_2": {
        "title": "和融世界 · 文脉生根",
        "title_en": "Harmony with the World · Rooted in Culture",
        "positive": (
            "大师级概念海报设计，纵向竖构图，垂直比例约3:4，"
            "海南自贸港主题原创文化视觉IP。"
            "一棵嵌有金色'和'字的生命之树贯穿天地。"
            "树根深扎土层，以金色浮雕质感铭刻海洋文化、侨乡文化、黎苗文化等海南多元文脉基因。"
            "树干融合鎏金流线、椰树树干肌理与海浪波纹，"
            "呈现鎏金配深蓝的东方科技美学风格。"
            "树冠由AI神经节点与金色枝蔓交织而成，舒展延伸。"
            "多语种问候(Hello、Bonjour、Hola、こんにちは、مرحباً、Xin chào)隐藏于树冠之中。"
            "顶部发光地球悬浮，树冠外侧如翅膀般展开，寓意链接全球。"
            "鎏金与深蓝色主色调，椰青绿与珍珠白点缀，"
            "超精细细节，史诗级视觉冲击，电影级灯光，8K超高分辨率，"
            "自贸港开放属性，文明传承与科技创新"
        ),
        "negative": (
            "文字模糊，元素堆砌杂乱，色彩失衡，低分辨率，"
            "模糊不清，变形扭曲，过度曝光，暗部细节丢失，"
            "构图倾斜，文化符号滥用，生硬堆砌，不协调"
        ),
        "style": "东方科技美学 (Oriental Tech Aesthetics)",
        "aspect_ratio": "3:4",
        "seed_recommendations": [2025, 2048, 4096, 8888],
        "cfg_scale": 7.5,
        "steps": 30,
    }
}

# ── 核心生成引擎 ──────────────────────────────────────

def generate_image(
    prompt: str,
    negative_prompt: str = "",
    model: str = CONFIG["model"],
    size: str = "1792x2304",      # 接近3:4竖构图
    quality: str = "hd",
    style: str = "vivid",
    n: int = 1,
    seed: Optional[int] = None,
) -> dict:
    """
    通过 API 生成图像。
    当前适配 OpenAI DALL·E 3 接口格式。
    如需切换至 Stability AI / Midjourney API，替换此函数体即可。
    """
    import openai

    client = openai.OpenAI(
        api_key=CONFIG["api_key"],
        base_url=CONFIG["api_base"],
    )

    # 构建增强提示词（含负向引导）
    enhanced_prompt = prompt
    if negative_prompt:
        enhanced_prompt = f"{prompt}\n\n避免以下问题：{negative_prompt}"

    params = {
        "model": model,
        "prompt": enhanced_prompt,
        "size": size,
        "quality": quality,
        "style": style,
        "n": n,
    }

    # DALL·E 3 不支持 seed 参数，留作扩展
    if seed is not None and "dall-e" not in model:
        params["seed"] = seed

    print(f"[INFO] 发送生成请求...")
    print(f"[INFO] 模型: {model}")
    print(f"[INFO] 尺寸: {size}")
    if seed:
        print(f"[INFO] 种子: {seed}")

    start_time = time.time()
    response = client.images.generate(**params)
    elapsed = time.time() - start_time

    result = {
        "success": True,
        "elapsed_seconds": round(elapsed, 2),
        "data": [],
        "params": params,
    }

    for img_data in response.data:
        item = {
            "url": img_data.url,
            "revised_prompt": img_data.revised_prompt,
        }
        result["data"].append(item)

    print(f"[INFO] 生成完成，耗时 {result['elapsed_seconds']} 秒")
    return result


def save_image_from_url(url: str, filepath: str) -> str:
    """下载 URL 图像到本地文件。"""
    import requests

    print(f"[INFO] 下载图像到: {filepath}")
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()

    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    return filepath


def save_metadata(work_key: str, result: dict, output_path: str):
    """保存生成参数与结果元数据。"""
    meta = {
        "work": work_key,
        "prompt_info": PROMPTS[work_key],
        "generation_params": result["params"],
        "generation_result": {
            "elapsed_seconds": result["elapsed_seconds"],
            "image_count": len(result["data"]),
        },
        "timestamp": datetime.now().isoformat(),
        "pipeline_version": "1.0",
    }

    meta_path = output_path.replace(".png", ".json").replace(".jpg", ".json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"[INFO] 元数据已保存: {meta_path}")


def run_workflow(
    work_key: str,
    seed: Optional[int] = None,
    upscale: Optional[str] = None,
):
    """运行单幅作品完整生成工作流。"""
    prompt_data = PROMPTS[work_key]
    safe_title = prompt_data["title"].replace(" ", "_").replace("·", "_")
    os.makedirs(CONFIG["output_dir"], exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_title}_{timestamp}.png"
    filepath = os.path.join(CONFIG["output_dir"], filename)

    print(f"\n{'='*60}")
    print(f"  开始生成: {prompt_data['title']}")
    print(f"  风格: {prompt_data['style']}")
    print(f"{'='*60}\n")

    # 步骤1：生成图像
    result = generate_image(
        prompt=prompt_data["positive"],
        negative_prompt=prompt_data["negative"],
        seed=seed,
    )

    if not result["success"] or not result["data"]:
        print("[ERROR] 生成失败")
        return

    # 步骤2：下载图像
    image_url = result["data"][0]["url"]
    save_image_from_url(image_url, filepath)
    print(f"[OK] 图像已保存: {filepath}")

    # 步骤3：保存元数据
    if CONFIG["save_metadata"]:
        save_metadata(work_key, result, filepath)

    # 步骤4：放大处理（可选）
    if upscale and CONFIG["upscale_enabled"]:
        upscale_image(filepath, upscale)

    print(f"\n[完成] {prompt_data['title']} 生成工作流结束\n")
    return filepath


def upscale_image(image_path: str, method: str = "4x"):
    """
    图像放大处理。
    生产环境可集成 Real-ESRGAN / SwinIR 等模型。
    此处预留接口，实际放大需安装相应引擎。
    """
    print(f"[INFO] 放大处理: {image_path} (method={method})")
    print(f"[INFO] 提示: 如需实际放大，请安装 Real-ESRGAN 并调用 upscale 接口")
    # 实际放大代码示例（需安装 realesrgan）：
    # from realesrgan import RealESRGANer
    # upscaler = RealESRGANer(scale=4, model_path='models/RealESRGAN_x4plus.pth')
    # upscaler.enhance(image_path, output_path=image_path.replace('.png', '_4x.png'))


def batch_generate(seeds: Optional[dict] = None):
    """批量生成多幅作品。"""
    results = {}
    for work_key in ["work_1", "work_2"]:
        seed = seeds.get(work_key) if seeds else None
        fp = run_workflow(work_key, seed=seed)
        results[work_key] = fp
    return results


# ── 命令行入口 ──────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI 概念海报生成工程脚本 — 文明之树系列"
    )
    parser.add_argument(
        "--work", "-w",
        type=str,
        default="all",
        choices=["1", "2", "all", "work_1", "work_2"],
        help="选择生成的作品：1=文明代码，2=和融世界，all=全部"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="随机种子（可选）"
    )
    parser.add_argument(
        "--upscale", "-u",
        type=str,
        default=None,
        choices=["4x", "2x"],
        help="放大倍数（需安装放大引擎）"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出目录（默认 ./outputs）"
    )

    args = parser.parse_args()

    if args.output:
        CONFIG["output_dir"] = args.output

    # 作品映射
    work_map = {
        "1": "work_1",
        "2": "work_2",
        "work_1": "work_1",
        "work_2": "work_2",
    }

    if args.work == "all":
        print(">>> 批量生成全部作品 <<<")
        seeds = {"work_1": args.seed or 42, "work_2": args.seed or 2025}
        batch_generate(seeds=seeds)
    else:
        work_key = work_map[args.work]
        run_workflow(work_key, seed=args.seed, upscale=args.upscale)


if __name__ == "__main__":
    main()
