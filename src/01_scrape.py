"""Faza 1: preuzimanje Yelp recenzija preko Apify actor-a (epicscrapers).

MODE = "preflight" -> svih 30, po 1 recenzija: provera URL-ova + broj recenzija (procena troška)
MODE = "test"      -> 2 restorana, sve recenzije (provera pre punog skidanja)
MODE = "full"      -> svih 30, sve recenzije od otvaranja, svi jezici
Sirov rezultat ide u data/raw/ i posle se ne menja.
"""
import json
from decimal import Decimal
from pathlib import Path

import pandas as pd
from apify_client import ApifyClient

ROOT = Path(__file__).resolve().parents[1]
ACTOR = "epicscrapers/yelp-reviews-scraper"
PRICE_PER_REVIEW = 0.00025  # USD, FREE nivo
MODE = "test"

# po režimu: koliko restorana, koliko recenzija po restoranu (0 = sve), gornja granica troška
SETTINGS = {
    "preflight": dict(n=30, max_reviews=1, cap="0.05"),
    "test": dict(n=2, max_reviews=0, cap="2"),
    "full": dict(n=30, max_reviews=0, cap="50"),
}


def read_token():
    # Token čitamo iz .env (koji je u .gitignore), nikad ga ne pišemo u kod
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("APIFY_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("APIFY_TOKEN nije pronađen u .env")


s = SETTINGS[MODE]
restaurants = pd.read_csv(ROOT / "data" / "restaurants.csv").head(s["n"])

run_input = {
    "businesses": list(restaurants["yelp_url"]),
    "maxReviewsPerBusiness": s["max_reviews"],
    "sortBy": "newest",
    "languages": [],               # prazno = svi jezici
    "includeReviewerDetails": True,  # reviewer ID, broj recenzija/prijatelja, Elite
}

client = ApifyClient(read_token())
run = client.actor(ACTOR).call(run_input=run_input, max_total_charge_usd=Decimal(s["cap"]))
print("status:", run.status)

# iterate_items preuzima rezultate u delovima (bitno za ~51.000 recenzija u "full")
items = list(client.dataset(run.default_dataset_id).iterate_items())
out = ROOT / "data" / "raw" / f"yelp_epicscrapers_{MODE}.json"
out.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{len(items)} recenzija -> {out}")

if MODE == "preflight":
    # Jedan red po restoranu: spajamo preko ulaznog URL-a ("input")
    biz = pd.DataFrame(items).drop_duplicates("input")[
        ["input", "businessName", "isBusinessClosed", "businessRating",
         "businessReviewCount", "businessPrice", "businessCategories"]]
    table = restaurants[["id", "restoran", "yelp_url"]].merge(
        biz, left_on="yelp_url", right_on="input", how="left")
    print(table.drop(columns=["yelp_url", "input"]).to_string(index=False))
    total = table["businessReviewCount"].sum()
    print(f"\nNije nađeno: {table['businessName'].isna().sum()} | "
          f"ukupno recenzija: {total:,.0f} | procena troška: ${total * PRICE_PER_REVIEW:.2f}")
