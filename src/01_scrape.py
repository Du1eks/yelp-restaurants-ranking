"""Faza 1: preuzimanje Yelp recenzija preko Apify actor-a.

TEST = True  -> 1 restoran, 20 recenzija (provera polja, par centi)
TEST = False -> svih 30 restorana, sve recenzije od 2022-01-01
Sirovi rezultat ide u data/raw/ i posle se ne menja.
"""
import json
from decimal import Decimal
from pathlib import Path

import pandas as pd
from apify_client import ApifyClient

ROOT = Path(__file__).resolve().parents[1]
ACTOR = "tri_angle/yelp-review-scraper"
TEST = True


def read_token():
    # Token čitamo iz .env (koji je u .gitignore), nikad ga ne pišemo u kod
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("APIFY_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("APIFY_TOKEN nije pronađen u .env")


restaurants = pd.read_csv(ROOT / "data" / "restaurants.csv")
if TEST:
    restaurants = restaurants.head(1)  # r01, Piccola Cucina Osteria

run_input = {
    "startUrls": [{"url": u} for u in restaurants["yelp_url"]],
    "language": "",  # sve jezike: ocena je ocena, bez obzira na jezik teksta
    "dateFrom": "2022-01-01",
}
if TEST:
    run_input["maxReviewsPerUrl"] = 20

client = ApifyClient(read_token())
# max_total_charge_usd = gornja granica troška, da run ne može da "pobegne"
run = client.actor(ACTOR).call(
    run_input=run_input,
    max_total_charge_usd=Decimal("0.50") if TEST else Decimal("40"),
)
print("status:", run.status)

items = client.dataset(run.default_dataset_id).list_items().items
name = "tri_angle_test_r01.json" if TEST else "tri_angle_reviews_2022_2026.json"
out = ROOT / "data" / "raw" / name
out.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{len(items)} recenzija -> {out}")
