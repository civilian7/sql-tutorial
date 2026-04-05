"""상품 이미지 데이터 생성 + 다운로드"""

from __future__ import annotations

import hashlib
import os
import time
from datetime import datetime, timedelta
from typing import Any
from urllib.request import urlopen, Request
from urllib.error import URLError
import json

from src.generators.base import BaseGenerator


# 카테고리 slug → Pexels 검색 키워드 매핑
CATEGORY_KEYWORDS = {
    "desktop-prebuilt": "desktop computer",
    "desktop-custom": "gaming PC setup",
    "desktop-barebone": "mini PC",
    "laptop-general": "laptop computer",
    "laptop-gaming": "gaming laptop",
    "laptop-2in1": "convertible laptop",
    "laptop-macbook": "macbook laptop",
    "monitor-general": "computer monitor",
    "monitor-gaming": "gaming monitor curved",
    "monitor-professional": "professional monitor",
    "cpu-intel": "computer processor CPU",
    "cpu-amd": "computer processor CPU",
    "mb-intel": "computer motherboard",
    "mb-amd": "computer motherboard",
    "ram-ddr4": "computer RAM memory",
    "ram-ddr5": "computer RAM memory",
    "storage-ssd": "SSD storage drive",
    "storage-hdd": "hard drive HDD",
    "storage-external": "external hard drive",
    "gpu-nvidia": "graphics card GPU",
    "gpu-amd": "graphics card GPU",
    "psu": "computer power supply",
    "case": "computer case tower",
    "cooling-air": "CPU cooler heatsink",
    "cooling-liquid": "liquid cooling AIO",
    "keyboard-mechanical": "mechanical keyboard",
    "keyboard-membrane": "computer keyboard",
    "keyboard-wireless": "wireless keyboard",
    "mouse-wired": "computer mouse",
    "mouse-wireless": "wireless mouse",
    "mouse-gaming": "gaming mouse",
    "audio": "headphones headset",
    "printer": "printer office",
    "network-router": "wifi router",
    "network-switch": "network switch",
    "network-nic": "network adapter card",
    "ups": "UPS battery backup",
    "software-os": "software box Windows",
    "software-office": "office software",
    "software-security": "antivirus software",
}

# 대분류 fallback
PARENT_KEYWORDS = {
    "desktop-pc": "desktop computer",
    "laptop": "laptop computer",
    "monitor": "computer monitor",
    "cpu": "computer processor",
    "motherboard": "motherboard",
    "ram": "RAM memory",
    "storage": "storage drive",
    "gpu": "graphics card",
    "cooling": "CPU cooler",
    "keyboard": "computer keyboard",
    "mouse": "computer mouse",
    "network": "network equipment",
    "software": "software",
}


class ImageGenerator(BaseGenerator):

    def generate_product_images(
        self,
        products: list[dict],
        categories: list[dict],
    ) -> list[dict]:
        """상품별 이미지 레코드를 생성한다 (URL은 placeholder)."""
        rows = []
        img_id = 0

        cat_slug_map = {c["id"]: c["slug"] for c in categories}

        for p in products:
            slug = cat_slug_map.get(p["category_id"], "")
            # 상품당 1~5장 (대부분 2~3장)
            num_images = self.rng.choices([1, 2, 3, 4, 5], weights=[15, 35, 30, 15, 5], k=1)[0]

            for i in range(num_images):
                img_id += 1
                created = datetime.strptime(p["created_at"], "%Y-%m-%d %H:%M:%S")
                img_created = created + timedelta(hours=self.rng.randint(0, 24))

                # 이미지 타입
                if i == 0:
                    image_type = "main"
                elif i == 1:
                    image_type = self.rng.choice(["angle", "side", "detail"])
                elif i == 2:
                    image_type = self.rng.choice(["back", "detail", "package"])
                else:
                    image_type = self.rng.choice(["lifestyle", "accessory", "size_comparison"])

                # placeholder URL (즉시 작동)
                name_encoded = p["name"].replace(" ", "+")[:50]
                image_url = f"https://placehold.co/800x800/f0f0f0/333?text={name_encoded}"

                # 파일명 (다운로드 시 사용)
                file_name = f"{p['id']}_{i+1}.jpg"

                rows.append({
                    "id": img_id,
                    "product_id": p["id"],
                    "image_url": image_url,
                    "file_name": file_name,
                    "image_type": image_type,
                    "alt_text": f"{p['brand']} {p['name']} - {image_type}",
                    "width": 800,
                    "height": 800,
                    "file_size": None,
                    "sort_order": i + 1,
                    "is_primary": 1 if i == 0 else 0,
                    "created_at": self.fmt_dt(img_created),
                })

        return rows


def download_images(
    products: list[dict],
    categories: list[dict],
    image_records: list[dict],
    output_dir: str,
    api_key: str,
    max_per_category: int = 15,
):
    """Pexels API로 카테고리별 이미지를 다운로드하고 DB 레코드를 업데이트한다."""
    img_dir = os.path.join(output_dir, "images")
    os.makedirs(img_dir, exist_ok=True)

    cat_slug_map = {c["id"]: c["slug"] for c in categories}

    # 카테고리별 상품 그룹
    prods_by_cat: dict[str, list[dict]] = {}
    for p in products:
        slug = cat_slug_map.get(p["category_id"], "unknown")
        prods_by_cat.setdefault(slug, []).append(p)

    # 카테고리별 이미지 다운로드
    cat_images: dict[str, list[str]] = {}  # slug → [local_path, ...]
    downloaded = 0

    for slug, prods in prods_by_cat.items():
        keyword = CATEGORY_KEYWORDS.get(slug, "")
        if not keyword:
            # 대분류 fallback
            parent_slug = slug.split("-")[0] if "-" in slug else slug
            keyword = PARENT_KEYWORDS.get(parent_slug, "computer technology")

        print(f"  [{slug}] '{keyword}' 검색 중... ({len(prods)}개 상품)")

        photos = _search_pexels(api_key, keyword, max_per_category)
        if not photos:
            print(f"    -> 결과 없음, fallback 'computer technology'")
            photos = _search_pexels(api_key, "computer technology", 5)

        paths = []
        for i, photo in enumerate(photos):
            # medium 크기 (800px 내외)
            url = photo.get("src", {}).get("medium", "")
            if not url:
                continue

            fname = f"cat_{slug}_{i+1}.jpg"
            fpath = os.path.join(img_dir, fname)

            if not os.path.exists(fpath):
                try:
                    _download_file(url, fpath)
                    downloaded += 1
                except Exception as e:
                    print(f"    다운로드 실패: {e}")
                    continue

            file_size = os.path.getsize(fpath)
            paths.append((fname, photo.get("width", 800), photo.get("height", 600), file_size))

        cat_images[slug] = paths
        print(f"    -> {len(paths)}장 확보")

        # API rate limit 준수
        time.sleep(0.5)

    # 이미지 레코드 업데이트
    updated = 0
    for rec in image_records:
        prod_id = rec["product_id"]
        prod = next((p for p in products if p["id"] == prod_id), None)
        if not prod:
            continue
        slug = cat_slug_map.get(prod["category_id"], "unknown")
        paths = cat_images.get(slug, [])
        if not paths:
            continue

        # 라운드 로빈으로 이미지 할당
        idx = (rec["sort_order"] - 1) % len(paths)
        fname, w, h, fsize = paths[idx]

        rec["image_url"] = f"images/{fname}"
        rec["file_name"] = fname
        rec["width"] = w
        rec["height"] = h
        rec["file_size"] = fsize
        updated += 1

    print(f"\n  다운로드: {downloaded}장, 레코드 업데이트: {updated}건")
    return image_records


def _search_pexels(api_key: str, query: str, per_page: int = 15) -> list[dict]:
    """Pexels API로 이미지를 검색한다."""
    url = f"https://api.pexels.com/v1/search?query={query}&per_page={per_page}&orientation=square"
    req = Request(url, headers={"Authorization": api_key})
    try:
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get("photos", [])
    except (URLError, Exception) as e:
        print(f"    API 오류: {e}")
        return []


def _download_file(url: str, path: str):
    """URL에서 파일을 다운로드한다."""
    req = Request(url, headers={"User-Agent": "TestDBGenerator/1.0"})
    with urlopen(req, timeout=30) as resp:
        with open(path, "wb") as f:
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                f.write(chunk)
