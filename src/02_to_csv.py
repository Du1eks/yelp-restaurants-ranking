"""Faza 2a: sirovi JSON (data/raw) -> CSV tabele (data/clean).

yelp_reviews.csv        - jedan red po Yelp recenziji
tripadvisor_reviews.csv - jedan red po TripAdvisor recenziji
restaurants.csv         - jedan red po restoranu: podaci sa obe platforme + zatvaranje
Sirovi JSON se ne menja. Tekst recenzija se čuva (po uputstvu mentora).
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, CLEAN = ROOT / "data" / "raw", ROOT / "data" / "clean"
# Murray's (r18): Bleecker St zatvoren ~2020-08; posle toga isti listing pokriva novi lokal u LIC
# (6sqft, 2020-08-20: LIC "replaces the former Murray's Cheese Bar on Bleecker Street")
MURRAYS_LIC_FROM = pd.Timestamp("2020-08-20", tz="UTC")


def load(name):
    with open(RAW / f"{name}.json", encoding="utf-8") as f:
        return pd.json_normalize(json.load(f))


def joined(lst):
    # lista -> tekst "a;b;c" (CSV ne može da čuva liste)
    return ";".join(str(x) for x in lst) if isinstance(lst, list) else ""


rest = pd.read_csv(ROOT / "data" / "restaurants.csv", dtype=str, keep_default_na=False)
rest["restaurant_id"] = rest["id"].str[1:].astype(int)  # r01 -> 1, redosled iz rada 2019
closed = pd.read_csv(ROOT / "data" / "closed_restaurants.csv", dtype=str, keep_default_na=False)

# ---------- Yelp ----------
y = load("yelp_full").merge(rest[["restaurant_id", "restoran", "yelp_url"]],
                            left_on="input", right_on="yelp_url", how="left")
assert y["restaurant_id"].notna().all(), "Yelp recenzija bez restorana"
y_date = pd.to_datetime(y["date"], utc=True)

yelp = pd.DataFrame({
    "restaurant_id": y["restaurant_id"],
    "name": y["restoran"],
    "yelp_url": y["yelp_url"],
    "review_id": y["reviewId"],
    "review_url": y["reviewUrl"],
    "review_date": y_date.dt.strftime("%Y-%m-%d"),
    "review_datetime_utc": y_date.dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "rating": y["rating"],
    "reviewer_id": y["reviewerId"],
    "reviewer_username": y["reviewerName"],
    "reviewer_profile_url": y["reviewerUrl"],
    "reviewer_location": y["reviewerLocation"],
    "reviewer_member_since": pd.to_datetime(y["reviewerMemberSince"], utc=True).dt.strftime("%Y-%m-%d"),
    "reviewer_review_count": y["reviewerReviewCount"],
    "reviewer_friends": y["reviewerFriendCount"],
    "reviewer_photos": y["reviewerPhotoCount"],
    "reviewer_checkins": y["reviewerCheckIns"],
    "reviewer_elite_now": y["isReviewerElite"],
    "reviewer_elite_years": y["reviewerEliteYears"].map(lambda l: joined(sorted(l))),
    "reviewer_elite_n_years": y["reviewerEliteYears"].map(len),
    "review_useful": y["usefulCount"],
    "review_funny": y["funnyCount"],
    "review_cool": y["coolCount"],
    "review_photos": y["photoCount"],
    "is_first_review": y["isFirstReview"],
    "is_edited": y["isEdited"],
    "n_previous_versions": y["previousVersions"].map(len),
    "owner_response": y["hasOwnerReply"],
    "owner_response_text": y["ownerReply"],
    "owner_response_author_role": y["ownerReplyAuthorRole"],
    "language": y["language"],
    "text": y["text"],
})
# Murray's: recenzije posle zatvaranja Bleecker-a su za LIC lokal -> posebno označene
yelp["location_period"] = "original"
yelp.loc[(yelp["restaurant_id"] == 18) & (y_date >= MURRAYS_LIC_FROM), "location_period"] = "murrays_lic"

# ---------- TripAdvisor ----------
t = load("tripadvisor_full")
t["locationId"] = t["locationId"].astype(str)
t = t.merge(rest[["restaurant_id", "restoran", "tripadvisor_id", "tripadvisor_url"]],
            left_on="locationId", right_on="tripadvisor_id", how="left")
assert t["restaurant_id"].notna().all(), "TripAdvisor recenzija bez restorana"

# subratings: lista [{label, value}] -> kolone subrating_value, subrating_service, ...
sub = t["subratings"].map(lambda l: {f"subrating_{d['label'].lower()}": d["value"] for d in l})
sub = pd.DataFrame(list(sub), index=t.index)

ta = pd.DataFrame({
    "restaurant_id": t["restaurant_id"],
    "name": t["restoran"],
    "tripadvisor_url": t["tripadvisor_url"],
    "review_id": t["id"],
    "review_url": t["reviewUrl"],
    "review_date": t["publishedDateISO"],
    "visit_date": t["dateVisitedISO"],
    "rating": t["rating"],
    "title": t["title"],
    "reviewer_id": t["author.userId"],
    "reviewer_username": t["author.username"],
    "reviewer_profile_url": t["author.profileUrl"],
    "reviewer_hometown": t["author.hometown"],
    "reviewer_contributions": t["author.totalContributions"],
    "reviewer_verified": t["author.isVerified"],
    "review_helpful_votes": t["helpfulVotes"],
    "trip_type": t["tripType"],
    "owner_response": t["ownerResponseDetail.text"].notna(),
    "owner_response_text": t["ownerResponseDetail.text"],
    "owner_response_date": t["ownerResponseDetail.publishedDate"],
    "owner_response_role": t["ownerResponseDetail.connectionToSubject"],
    "language": t["language"],
    "original_language": t["originalLanguage"],
    "is_translated": t["isTranslated"],
    "translation_type": t["translationType"],
    "tip_text": t["tipText"],
    "text": t["text"],
}).join(sub)

# ---------- Restorani (jedan red po restoranu) ----------
yb = y.groupby("restaurant_id").agg(
    yelp_business_id=("businessId", "first"),
    address=("businessAddress", "first"),
    yelp_closed=("isBusinessClosed", "first"),
    yelp_displayed_rating=("businessRating", "first"),
    yelp_displayed_review_count=("businessReviewCount", "first"),
    yelp_price=("businessPrice", "first"),
    yelp_categories=("businessCategories", lambda s: joined(s.iloc[0])),
    **{f"yelp_stars_{k}": (f"businessRatingCounts.{k}", "first") for k in "12345"},
    yelp_scraped_reviews=("reviewId", "size"),
    yelp_checked_at=("scrapedAt", lambda s: s.min()[:10]),
)
yr = yelp.groupby("restaurant_id")["review_date"].agg(yelp_first_review="min", yelp_last_review="max")
tr = ta.groupby("restaurant_id").agg(ta_scraped_reviews=("review_id", "size"),
                                     ta_first_review=("review_date", "min"),
                                     ta_last_review=("review_date", "max"))

restaurants = (rest[["restaurant_id", "id", "restoran", "yelp_url", "tripadvisor_id", "tripadvisor_url", "napomena"]]
               .rename(columns={"restoran": "name", "napomena": "note"})
               .merge(yb, on="restaurant_id", how="left").merge(yr, on="restaurant_id", how="left")
               .merge(tr, on="restaurant_id", how="left"))
restaurants["ta_scraped_reviews"] = restaurants["ta_scraped_reviews"].fillna(0).astype(int)
restaurants["ta_available"] = restaurants["ta_scraped_reviews"] > 0
# Spice Symphony (r13, r14): TA je spojio dve lokacije -> nije isti entitet kao na Yelp-u (mentor 2026-10-19)
restaurants["in_platform_comparison"] = restaurants["ta_available"] & ~restaurants["id"].isin(["r13", "r14"])
restaurants = restaurants.merge(
    closed[["id", "zatvoren_procena", "najranije", "najkasnije", "pouzdanost", "izvor"]]
    .rename(columns={"zatvoren_procena": "closure_estimate", "najranije": "closure_earliest",
                     "najkasnije": "closure_latest", "pouzdanost": "closure_confidence", "izvor": "closure_source"}),
    on="id", how="left")
restaurants["yelp_claimed"] = ""  # nijedan actor ne vraća -> ručno sa Yelp stranice
restaurants["awards"] = ""        # npr. Travellers' Choice -> ručno

# ---------- Čuvanje ----------
# utf-8-sig: Excel ispravno prikazuje slova kao ú, ć (ne remeti pandas/R)
CLEAN.mkdir(exist_ok=True)
for name, df in [("yelp_reviews", yelp), ("tripadvisor_reviews", ta), ("restaurants", restaurants)]:
    df.to_csv(CLEAN / f"{name}.csv", index=False, encoding="utf-8-sig")
    print(f"{name}.csv: {len(df):,} redova, {df.shape[1]} kolona")
