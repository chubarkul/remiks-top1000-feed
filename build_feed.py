#!/usr/bin/env python3
"""Собирает feed.xml (Google Merchant RSS) из feed.csv — топ-1000 товаров Remiks
по продажам за 7 дней. Картинки берутся из images/<id>.jpg в этом же репозитории.
"""
import csv
from datetime import datetime, timezone
from xml.sax.saxutils import escape

REPO_RAW = "https://raw.githubusercontent.com/chubarkul/remiks-top1000-feed/main"
CURRENCY = "RSD"
GENDER = {
    "Muškarci": "male",
    "Dečaci": "male",
    "Žene": "female",
    "Devojčice": "female",
    "Unisex": "unisex",
    "Deca": "unisex",
}

csv.field_size_limit(10 ** 9)


def tag(name, value):
    return f"      <{name}>{escape(str(value))}</{name}>\n"


def main():
    with open("feed.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    built = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">\n',
        "  <channel>\n",
        "    <title>Remiks — Top 1000 (7d sales)</title>\n",
        "    <link>https://remiks.com</link>\n",
        "    <description>Топ-1000 товаров Remiks по продажам за 7 дней. "
        "Картинки — локальные, из этого репозитория.</description>\n",
        f"    <lastBuildDate>{built}</lastBuildDate>\n",
    ]

    for r in rows:
        out.append("    <item>\n")
        out.append(tag("g:id", r["id"]))
        out.append(tag("title", r["title"]))
        out.append(tag("description", r["description"] or r["title"]))
        out.append(tag("link", r["link"]))
        out.append(tag("g:image_link", f"{REPO_RAW}/images/{r['id']}.jpg"))
        out.append(tag("g:availability", r["availability"]))
        out.append(tag("g:condition", r["condition"] or "new"))
        out.append(tag("g:price", f"{float(r['price']):.2f} {CURRENCY}"))
        if r["sale_price"].strip():
            out.append(tag("g:sale_price", f"{float(r['sale_price']):.2f} {CURRENCY}"))
        if r["brand"].strip():
            out.append(tag("g:brand", r["brand"]))
        if GENDER.get(r["gender"]):
            out.append(tag("g:gender", GENDER[r["gender"]]))
        if r["color"].strip():
            out.append(tag("g:color", r["color"]))
        product_type = " > ".join(
            v for v in (r["custom_label_0"], r["custom_label_1"]) if v.strip()
        )
        if product_type:
            out.append(tag("g:product_type", product_type))
        for i in range(5):
            v = r[f"custom_label_{i}"]
            if v.strip():
                out.append(tag(f"g:custom_label_{i}", v))
        out.append("    </item>\n")

    out.append("  </channel>\n</rss>\n")

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.writelines(out)
    print(f"feed.xml: {len(rows)} items")


if __name__ == "__main__":
    main()
