#!/usr/bin/env python3
"""
AI 姒傚康娴锋姤鐢熸垚宸ョ▼鑴氭湰
========================
浣滃搧锛氥€婃枃鏄庝唬鐮侊細浠庣敳楠ㄥ埌AI銆?& 銆婂拰铻嶄笘鐣屄锋枃鑴夌敓鏍广€?姣旇禌锛欰I 鍒涗綔澶ц禌
鐜锛歅ython 3.10+

渚濊禆瀹夎锛?    pip install openai pillow requests

浣跨敤鏂瑰紡锛?    python generate_poster.py --work 1        # 鐢熸垚浣滃搧涓€
    python generate_poster.py --work 2        # 鐢熸垚浣滃搧浜?    python generate_poster.py --work all      # 鐢熸垚鍏ㄩ儴
    python generate_poster.py --work 1 --upscale 4x  # 鐢熸垚骞舵斁澶?"""

import os
import json
import argparse
import time
from datetime import datetime
from typing import Optional

# 鈹€鈹€ 閰嶇疆 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
CONFIG = {
    # API 閰嶇疆锛堣鏇挎崲涓哄疄闄?API Key 鍜?endpoint锛?    "api_key": os.environ.get("AI_API_KEY", "YOUR_API_KEY_HERE"),
    "api_base": os.environ.get("AI_API_BASE", "https://api.openai.com/v1"),
    "model": "dall-e-3",                  # 鎴?stability-ai/stable-diffusion-3

    # 杈撳嚭閰嶇疆
    "output_dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs"),
    "save_metadata": True,                 # 姣忔鐢熸垚鑷姩淇濆瓨鍙傛暟鍏冩暟鎹?
    # 鏀惧ぇ閰嶇疆
    "upscale_enabled": True,
    "upscale_method": "esrgan",            # esrgan / real-esrgan
}

# 鈹€鈹€ Prompt 妯℃澘搴?鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

PROMPTS = {
    "work_1": {
        "title": "鏂囨槑浠ｇ爜锛氫粠鐢查鍒癆I",
        "title_en": "The Civilization Code: From Oracle to AI",
        "positive": (
            "澶у笀绾ф蹇垫捣鎶ヨ璁★紝绾靛悜绔栨瀯鍥撅紝鍨傜洿姣斾緥绾?:4锛?
            "涓€妫靛法澶х殑鏂囨槑涔嬫爲璐┛澶╁湴銆?
            "鏍戞牴娣卞煁浜庝腑鍗庢枃鏄庡湡澹や箣涓紝鏍圭郴鐢辩敳楠ㄦ枃銆侀噾鏂囥€佺瘑涔︺€佺绠€銆佸彜绫嶇汗鏍风粍鎴愶紝"
            "鏁ｅ彂鍙よ€侀噾鑹插厜鑺掋€?
            "鏂囧瓧閫愭笎婕斿寲锛屾爲鏍瑰悜涓婂欢浼告椂鑷劧杞寲涓轰簩杩涘埗浠ｇ爜0鍜?锛?
            "鍐嶈浆鍖栦负鍙戝厜鐨勬暟鎹祦涓庣缁忕綉缁滅粨鏋勩€?
            "鏍戝共铻嶅悎姘村ⅷ鑲岀悊銆侀潚閾滃櫒绾规牱銆佺ゥ浜戠汗楗颁笌鏈潵绉戞妧鐢佃矾绾圭悊锛?
            "杩滅湅鏄爲鐨紝杩戠湅闅愮害鍛堢幇闀垮煄杞粨銆?
            "鏍戝啝鐢辨棤鏁癆I绁炵粡鑺傜偣銆佹暟瀛楀厜鐐瑰拰鍙戝厜缃戠粶缁勬垚锛屽悜鍏ㄧ悆寤跺睍銆?
            "椤堕儴鎮诞鍙戝厜鍦扮悆锛岃繛鎺ヤ笘鐣屽悇澶ф床銆?
            "鏍戝啝涓殣钘忓鍥借瑷€'浣犲ソ'锛屽寘鎷琀ello銆丅onjour銆丠ola銆併亾銈撱伀銇°伅銆佡呚必ㄘз嬨€?
            "閲戣壊涓庢繁钃濊壊涓昏壊璋冿紝涓滄柟缇庡涓庢湭鏉ョ鎶€铻嶅悎锛?
            "瓒呯簿缁嗙粏鑺傦紝鍙茶瘲绾ц瑙夊啿鍑伙紝鐢靛奖绾х伅鍏夛紝8K瓒呴珮鍒嗚鲸鐜囷紝"
            "鍏ㄧ悆浼犳挱涓婚锛屾枃鏄庝紶鎵夸笌绉戞妧鍒涙柊锛屽浗闄呰璁″ぇ濂栭鏍?
        ),
        "negative": (
            "鏂囧瓧妯＄硦锛屽厓绱犲爢鐮屾潅涔憋紝鑹插僵澶辫　锛屼綆鍒嗚鲸鐜囷紝"
            "妯＄硦涓嶆竻锛屽彉褰㈡壄鏇诧紝杩囧害鏇濆厜锛屾殫閮ㄧ粏鑺備涪澶憋紝"
            "鏋勫浘鍊炬枩锛岃タ鏂逛腑蹇冭瑙掞紝鏂囧寲绗﹀彿婊ョ敤锛屼笉鍗忚皟"
        ),
        "style": "涓滄柟缇庡 脳 璧涘崥鏈潵 (Cyber-Orientalism)",
        "aspect_ratio": "3:4",
        "seed_recommendations": [42, 128, 256, 512, 1024],
        "cfg_scale": 7.5,
        "steps": 30,
    },
    "work_2": {
        "title": "鍜岃瀺涓栫晫 路 鏂囪剦鐢熸牴",
        "title_en": "Harmony with the World 路 Rooted in Culture",
        "positive": (
            "澶у笀绾ф蹇垫捣鎶ヨ璁★紝绾靛悜绔栨瀯鍥撅紝鍨傜洿姣斾緥绾?:4锛?
            "娴峰崡鑷锤娓富棰樺師鍒涙枃鍖栬瑙塈P銆?
            "涓€妫靛祵鏈夐噾鑹?鍜?瀛楃殑鐢熷懡涔嬫爲璐┛澶╁湴銆?
            "鏍戞牴娣辨墡鍦熷眰锛屼互閲戣壊娴洉璐ㄦ劅閾埢娴锋磱鏂囧寲銆佷鲸涔℃枃鍖栥€侀粠鑻楁枃鍖栫瓑娴峰崡澶氬厓鏂囪剦鍩哄洜銆?
            "鏍戝共铻嶅悎閹忛噾娴佺嚎銆佹ぐ鏍戞爲骞茶倢鐞嗕笌娴锋氮娉㈢汗锛?
            "鍛堢幇閹忛噾閰嶆繁钃濈殑涓滄柟绉戞妧缇庡椋庢牸銆?
            "鏍戝啝鐢盇I绁炵粡鑺傜偣涓庨噾鑹叉灊钄撲氦缁囪€屾垚锛岃垝灞曞欢浼搞€?
            "澶氳绉嶉棶鍊?Hello銆丅onjour銆丠ola銆併亾銈撱伀銇°伅銆佡呚必ㄘз嬨€乆in ch脿o)闅愯棌浜庢爲鍐犱箣涓€?
            "椤堕儴鍙戝厜鍦扮悆鎮诞锛屾爲鍐犲渚у缈呰唨鑸睍寮€锛屽瘬鎰忛摼鎺ュ叏鐞冦€?
            "閹忛噾涓庢繁钃濊壊涓昏壊璋冿紝妞伴潚缁夸笌鐝嶇彔鐧界偣缂€锛?
            "瓒呯簿缁嗙粏鑺傦紝鍙茶瘲绾ц瑙夊啿鍑伙紝鐢靛奖绾х伅鍏夛紝8K瓒呴珮鍒嗚鲸鐜囷紝"
            "鑷锤娓紑鏀惧睘鎬э紝鏂囨槑浼犳壙涓庣鎶€鍒涙柊"
        ),
        "negative": (
            "鏂囧瓧妯＄硦锛屽厓绱犲爢鐮屾潅涔憋紝鑹插僵澶辫　锛屼綆鍒嗚鲸鐜囷紝"
            "妯＄硦涓嶆竻锛屽彉褰㈡壄鏇诧紝杩囧害鏇濆厜锛屾殫閮ㄧ粏鑺備涪澶憋紝"
            "鏋勫浘鍊炬枩锛屾枃鍖栫鍙锋互鐢紝鐢熺‖鍫嗙爩锛屼笉鍗忚皟"
        ),
        "style": "涓滄柟绉戞妧缇庡 (Oriental Tech Aesthetics)",
        "aspect_ratio": "3:4",
        "seed_recommendations": [2025, 2048, 4096, 8888],
        "cfg_scale": 7.5,
        "steps": 30,
    }
}

# 鈹€鈹€ 鏍稿績鐢熸垚寮曟搸 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def generate_image(
    prompt: str,
    negative_prompt: str = "",
    model: str = CONFIG["model"],
    size: str = "1792x2304",      # 鎺ヨ繎3:4绔栨瀯鍥?    quality: str = "hd",
    style: str = "vivid",
    n: int = 1,
    seed: Optional[int] = None,
) -> dict:
    """
    閫氳繃 API 鐢熸垚鍥惧儚銆?    褰撳墠閫傞厤 OpenAI DALL路E 3 鎺ュ彛鏍煎紡銆?    濡傞渶鍒囨崲鑷?Stability AI / Midjourney API锛屾浛鎹㈡鍑芥暟浣撳嵆鍙€?    """
    import openai

    client = openai.OpenAI(
        api_key=CONFIG["api_key"],
        base_url=CONFIG["api_base"],
    )

    # 鏋勫缓澧炲己鎻愮ず璇嶏紙鍚礋鍚戝紩瀵硷級
    enhanced_prompt = prompt
    if negative_prompt:
        enhanced_prompt = f"{prompt}\n\n閬垮厤浠ヤ笅闂锛歿negative_prompt}"

    params = {
        "model": model,
        "prompt": enhanced_prompt,
        "size": size,
        "quality": quality,
        "style": style,
        "n": n,
    }

    # DALL路E 3 涓嶆敮鎸?seed 鍙傛暟锛岀暀浣滄墿灞?    if seed is not None and "dall-e" not in model:
        params["seed"] = seed

    print(f"[INFO] 鍙戦€佺敓鎴愯姹?..")
    print(f"[INFO] 妯″瀷: {model}")
    print(f"[INFO] 灏哄: {size}")
    if seed:
        print(f"[INFO] 绉嶅瓙: {seed}")

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

    print(f"[INFO] 鐢熸垚瀹屾垚锛岃€楁椂 {result['elapsed_seconds']} 绉?)
    return result


def save_image_from_url(url: str, filepath: str) -> str:
    """涓嬭浇 URL 鍥惧儚鍒版湰鍦版枃浠躲€?""
    import requests

    print(f"[INFO] 涓嬭浇鍥惧儚鍒? {filepath}")
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()

    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    return filepath


def save_metadata(work_key: str, result: dict, output_path: str):
    """淇濆瓨鐢熸垚鍙傛暟涓庣粨鏋滃厓鏁版嵁銆?""
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
    print(f"[INFO] 鍏冩暟鎹凡淇濆瓨: {meta_path}")


def run_workflow(
    work_key: str,
    seed: Optional[int] = None,
    upscale: Optional[str] = None,
):
    """杩愯鍗曞箙浣滃搧瀹屾暣鐢熸垚宸ヤ綔娴併€?""
    prompt_data = PROMPTS[work_key]
    safe_title = prompt_data["title"].replace(" ", "_").replace("路", "_")
    os.makedirs(CONFIG["output_dir"], exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_title}_{timestamp}.png"
    filepath = os.path.join(CONFIG["output_dir"], filename)

    print(f"\n{'='*60}")
    print(f"  寮€濮嬬敓鎴? {prompt_data['title']}")
    print(f"  椋庢牸: {prompt_data['style']}")
    print(f"{'='*60}\n")

    # 姝ラ1锛氱敓鎴愬浘鍍?    result = generate_image(
        prompt=prompt_data["positive"],
        negative_prompt=prompt_data["negative"],
        seed=seed,
    )

    if not result["success"] or not result["data"]:
        print("[ERROR] 鐢熸垚澶辫触")
        return

    # 姝ラ2锛氫笅杞藉浘鍍?    image_url = result["data"][0]["url"]
    save_image_from_url(image_url, filepath)
    print(f"[OK] 鍥惧儚宸蹭繚瀛? {filepath}")

    # 姝ラ3锛氫繚瀛樺厓鏁版嵁
    if CONFIG["save_metadata"]:
        save_metadata(work_key, result, filepath)

    # 姝ラ4锛氭斁澶у鐞嗭紙鍙€夛級
    if upscale and CONFIG["upscale_enabled"]:
        upscale_image(filepath, upscale)

    print(f"\n[瀹屾垚] {prompt_data['title']} 鐢熸垚宸ヤ綔娴佺粨鏉焅n")
    return filepath


def upscale_image(image_path: str, method: str = "4x"):
    """
    鍥惧儚鏀惧ぇ澶勭悊銆?    鐢熶骇鐜鍙泦鎴?Real-ESRGAN / SwinIR 绛夋ā鍨嬨€?    姝ゅ棰勭暀鎺ュ彛锛屽疄闄呮斁澶ч渶瀹夎鐩稿簲寮曟搸銆?    """
    print(f"[INFO] 鏀惧ぇ澶勭悊: {image_path} (method={method})")
    print(f"[INFO] 鎻愮ず: 濡傞渶瀹為檯鏀惧ぇ锛岃瀹夎 Real-ESRGAN 骞惰皟鐢?upscale 鎺ュ彛")
    # 瀹為檯鏀惧ぇ浠ｇ爜绀轰緥锛堥渶瀹夎 realesrgan锛夛細
    # from realesrgan import RealESRGANer
    # upscaler = RealESRGANer(scale=4, model_path='models/RealESRGAN_x4plus.pth')
    # upscaler.enhance(image_path, output_path=image_path.replace('.png', '_4x.png'))


def batch_generate(seeds: Optional[dict] = None):
    """鎵归噺鐢熸垚澶氬箙浣滃搧銆?""
    results = {}
    for work_key in ["work_1", "work_2"]:
        seed = seeds.get(work_key) if seeds else None
        fp = run_workflow(work_key, seed=seed)
        results[work_key] = fp
    return results


# 鈹€鈹€ 鍛戒护琛屽叆鍙?鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def main():
    parser = argparse.ArgumentParser(
        description="AI 姒傚康娴锋姤鐢熸垚宸ョ▼鑴氭湰 鈥?鏂囨槑涔嬫爲绯诲垪"
    )
    parser.add_argument(
        "--work", "-w",
        type=str,
        default="all",
        choices=["1", "2", "all", "work_1", "work_2"],
        help="閫夋嫨鐢熸垚鐨勪綔鍝侊細1=鏂囨槑浠ｇ爜锛?=鍜岃瀺涓栫晫锛宎ll=鍏ㄩ儴"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="闅忔満绉嶅瓙锛堝彲閫夛級"
    )
    parser.add_argument(
        "--upscale", "-u",
        type=str,
        default=None,
        choices=["4x", "2x"],
        help="鏀惧ぇ鍊嶆暟锛堥渶瀹夎鏀惧ぇ寮曟搸锛?
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="杈撳嚭鐩綍锛堥粯璁?./outputs锛?
    )

    args = parser.parse_args()

    if args.output:
        CONFIG["output_dir"] = args.output

    # 浣滃搧鏄犲皠
    work_map = {
        "1": "work_1",
        "2": "work_2",
        "work_1": "work_1",
        "work_2": "work_2",
    }

    if args.work == "all":
        print(">>> 鎵归噺鐢熸垚鍏ㄩ儴浣滃搧 <<<")
        seeds = {"work_1": args.seed or 42, "work_2": args.seed or 2025}
        batch_generate(seeds=seeds)
    else:
        work_key = work_map[args.work]
        run_workflow(work_key, seed=args.seed, upscale=args.upscale)


if __name__ == "__main__":
    main()
