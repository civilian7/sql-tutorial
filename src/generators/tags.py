"""Product tag generation -- for M:N relationship, EXISTS/IN, INTERSECT practice"""

from __future__ import annotations

import random
from typing import Any

from src.generators.base import BaseGenerator


# Category slug prefix -> related tag mapping
CATEGORY_TAG_MAP: dict[str, list[str]] = {
    "desktop": ["데스크톱", "본체", "고성능"],
    "laptop": ["노트북", "휴대용"],
    "monitor": ["모니터", "디스플레이"],
    "cpu": ["CPU", "프로세서"],
    "mb": ["메인보드"],
    "ram": ["메모리", "RAM"],
    "storage": ["저장장치"],
    "gpu": ["그래픽카드", "GPU"],
    "psu": ["파워서플라이"],
    "case": ["케이스"],
    "cooling": ["쿨링", "냉각"],
    "keyboard": ["키보드", "입력장치"],
    "mouse": ["마우스", "입력장치"],
    "audio": ["오디오", "사운드"],
    "printer": ["프린터", "출력장치"],
    "network": ["네트워크", "통신"],
    "ups": ["UPS", "전원보호"],
    "software": ["소프트웨어"],
}

# Tag master: (name, category)
TAG_MASTER: list[tuple[str, str]] = [
    # feature -- product characteristics
    ("RGB 라이팅", "feature"),
    ("저소음", "feature"),
    ("무선", "feature"),
    ("유선", "feature"),
    ("블루투스", "feature"),
    ("USB-C", "feature"),
    ("방수/방진", "feature"),
    ("OLED", "feature"),
    ("4K", "feature"),
    ("QHD", "feature"),
    ("FHD", "feature"),
    ("고주사율", "feature"),
    ("핫스왑", "feature"),
    ("모듈러", "feature"),
    ("Wi-Fi 7", "feature"),
    ("Wi-Fi 6E", "feature"),
    ("PCIe 5.0", "feature"),
    ("PCIe 4.0", "feature"),
    ("DDR5", "feature"),
    ("NVMe", "feature"),
    ("터치스크린", "feature"),
    ("에르고노믹", "feature"),
    # use_case -- intended use
    ("게이밍", "use_case"),
    ("사무용", "use_case"),
    ("영상편집", "use_case"),
    ("프로그래밍", "use_case"),
    ("그래픽디자인", "use_case"),
    ("학생용", "use_case"),
    ("서버/NAS", "use_case"),
    ("스트리밍", "use_case"),
    ("재택근무", "use_case"),
    ("휴대용", "use_case"),
    # target -- audience
    ("입문자용", "target"),
    ("전문가용", "target"),
    ("가성비", "target"),
    ("프리미엄", "target"),
    ("하이엔드", "target"),
    ("신제품", "target"),
    ("베스트셀러", "target"),
    ("한정판", "target"),
    # spec -- specifications
    ("경량", "spec"),
    ("대용량", "spec"),
    ("고효율", "spec"),
    ("오버클럭", "spec"),
    ("멀티코어", "spec"),
    ("듀얼채널", "spec"),
]


class TagGenerator(BaseGenerator):

    def generate_tags(self) -> list[dict]:
        """Generate the tag master list."""
        tag_map = self.locale.get("tags", {})
        rows = []
        for i, (name, cat) in enumerate(TAG_MASTER, start=1):
            translated = tag_map.get(name, name)
            rows.append({"id": i, "name": translated, "category": cat})
        return rows

    def generate_product_tags(
        self, products: list[dict], categories: list[dict],
    ) -> list[dict]:
        """Assign tags to each product (2-6 tags per product)."""
        rows = []
        cat_slug_map = {c["id"]: c["slug"] for c in categories}
        tag_by_name = {name: i + 1 for i, (name, _) in enumerate(TAG_MASTER)}
        all_tag_ids = list(range(1, len(TAG_MASTER) + 1))

        for p in products:
            slug = cat_slug_map.get(p["category_id"], "")
            prefix = slug.split("-")[0] if "-" in slug else slug

            # Category-related tags + random tags
            related_names = CATEGORY_TAG_MAP.get(prefix, [])
            related_ids = [tag_by_name[n] for n in related_names if n in tag_by_name]

            num_tags = self.rng.randint(2, 6)
            # Prioritize related tags, fill remainder randomly
            chosen = set(related_ids[:2])
            remaining = [tid for tid in all_tag_ids if tid not in chosen]
            extra = self.rng.sample(remaining, min(num_tags - len(chosen), len(remaining)))
            chosen.update(extra)

            # Add price-based tags
            if p["price"] >= 2000000:
                if "하이엔드" in tag_by_name:
                    chosen.add(tag_by_name["하이엔드"])
            elif p["price"] >= 1000000:
                if "프리미엄" in tag_by_name:
                    chosen.add(tag_by_name["프리미엄"])
            elif p["price"] <= 100000:
                if "가성비" in tag_by_name:
                    chosen.add(tag_by_name["가성비"])

            # Gaming category
            if "gaming" in slug:
                if "게이밍" in tag_by_name:
                    chosen.add(tag_by_name["게이밍"])

            for tid in sorted(chosen):
                rows.append({"product_id": p["id"], "tag_id": tid})

        return rows
