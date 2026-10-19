"""Faza 1: preuzimanje recenzija preko Apify actor-a (Yelp i TripAdvisor).

PLATFORM = "yelp"        -> epicscrapers/yelp-reviews-scraper
PLATFORM = "tripadvisor" -> kaix/tripadvisor-reviews-scraper
MODE = "preflight" -> svih 30, po 1 recenzija: provera URL-ova + broj recenzija (samo Yelp)
MODE = "test"      -> 2 restorana, sve recenzije (provera pre punog skidanja)
MODE = "full"      -> svi restorani, sve recenzije od otvaranja, svi jezici
Sirov rezultat ide u data/raw/ i posle se ne menja.
"""
import json
from decimal import Decimal
from pathlib import Path

import pandas as pd
from apify_client import ApifyClient

ROOT = Path(__file__).resolve().parents[1]
PLATFORM = "tripadvisor"
MODE = "full"

# po režimu: koliko restorana, koliko recenzija po restoranu (0 = sve)
MODES = {
    "preflight": dict(n=30, max_reviews=1),
    "test": dict(n=2, max_reviews=0),
    "full": dict(n=30, max_reviews=0),
}

# po platformi: actor, kolona sa adresom restorana, gornja granica troška (USD) po režimu
PLATFORMS = {
    "yelp": dict(actor="epicscrapers/yelp-reviews-scraper", key="yelp_url",
                 cap={"preflight": "0.05", "test": "2", "full": "15"}),
    "tripadvisor": dict(actor="kaix/tripadvisor-reviews-scraper", key="tripadvisor_id",
                        cap={"test": "1", "full": "3.5"}),
}


def read_token():
    # Token čitamo iz .env (koji je u .gitignore), nikad ga ne pišemo u kod
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("APIFY_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("APIFY_TOKEN nije pronađen u .env")


def build_input(targets, max_reviews):
    # Svaki actor ima svoja imena parametara; značenje je isto: ovi restorani, sve recenzije, svi jezici
    if PLATFORM == "yelp":
        return {"businesses": targets, "maxReviewsPerBusiness": max_reviews, "sortBy": "newest",
                "languages": [], "includeReviewerDetails": True}
    return {"businesses": targets, "maxReviews": max_reviews, "language": "all"}


m, p = MODES[MODE], PLATFORMS[PLATFORM]
restaurants = pd.read_csv(ROOT / "data" / "restaurants.csv", dtype=str, keep_default_na=False)
restaurants = restaurants[restaurants[p["key"]] != ""].head(m["n"])  # r13 nema TripAdvisor listing
print(f"{PLATFORM} / {MODE}: {len(restaurants)} restorana")

client = ApifyClient(read_token())
run = client.actor(p["actor"]).call(run_input=build_input(list(restaurants[p["key"]]), m["max_reviews"]),
                                    max_total_charge_usd=Decimal(p["cap"][MODE]))
print("status:", run.status)

# iterate_items preuzima rezultate u delovima (bitno za desetine hiljada recenzija)
items = list(client.dataset(run.default_dataset_id).iterate_items())
out = ROOT / "data" / "raw" / f"{PLATFORM}_{MODE}.json"
out.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{len(items)} recenzija -> {out}")

if PLATFORM == "yelp" and MODE == "preflight":
    # Jedan red po restoranu: spajamo preko ulaznog URL-a ("input")
    biz = pd.DataFrame(items).drop_duplicates("input")[
        ["input", "businessName", "isBusinessClosed", "businessRating",
         "businessReviewCount", "businessPrice", "businessCategories"]]
    table = restaurants[["id", "restoran", "yelp_url"]].merge(
        biz, left_on="yelp_url", right_on="input", how="left")
    print(table.drop(columns=["yelp_url", "input"]).to_string(index=False))
    total = table["businessReviewCount"].sum()
    print(f"\nNije nađeno: {table['businessName'].isna().sum()} | "
          f"ukupno recenzija: {total:,.0f} | procena troška: ${total * 0.00025:.2f}")
