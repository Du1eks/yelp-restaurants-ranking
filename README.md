# Yelp & TripAdvisor Restaurant Ranking (NYC)

Data collection and preparation for a research project in the Statistics Lab at the Faculty of Organizational Sciences (FON), University of Belgrade.

The project asks whether the rankings that review platforms show can be trusted. Yelp and TripAdvisor rank restaurants by the plain average of their ratings, so every review counts the same. The idea is to build a composite ranking that also accounts for **how credible the reviewer is** and **how reliable the estimate is**, then test whether that ranking predicts a restaurant's later performance (new ratings, review volume, closure) better than the platform's own ranking.

This repository covers the data side: choosing the sample, collecting every review from both platforms, cleaning it into analysis-ready tables, and documenting the closures.

## Sample

- **30 New York City restaurants** taken from an earlier study (2019) of the top-ranked NYC restaurants.
- The list was fixed **before** the period being analyzed, so the sample does not depend on how the restaurants performed later. A "current top 30" would only contain survivors (survivorship bias), and historical Yelp rankings are not stored anywhere.
- **All 30 are kept, including the 5 that have since closed.** Closure is one of the outcomes the ranking should predict.

## Data collection

Reviews were collected on 19 Oct 2026 with [Apify](https://apify.com) actors, because both platforms block direct scraping. For each restaurant the collection includes **every review since it opened, in every language, with no date or count limit**.

| | Yelp | TripAdvisor |
|---|---|---|
| Actor | `epicscrapers/yelp-reviews-scraper` | `kaix/tripadvisor-reviews-scraper` |
| Restaurants | 30 | 25 with reviews (29 requested) |
| Reviews | 51,029 | 47,545 |
| Date range | 2004 – Oct 2026 | 2004 – Oct 2026 |

Checks before the full run:
- On 2 test restaurants per platform, the number of collected reviews matched the count shown on the page.
- The Yelp actor returned the same review and reviewer IDs as a second, independent actor.
- No duplicate review IDs and no reviews without a date.

Fields kept per review include the rating, date, language, review text, owner response, and reviewer signals: number of reviews or contributions, friends, photos, Elite years (Yelp), plus useful/funny/cool and helpful votes.

## Closed restaurants

| Restaurant | Estimated closure | Evidence |
|---|---|---|
| Murray's Cheese Bar (Bleecker St) | ~Aug 2020 | Replaced by a new location in Long Island City |
| Piccola Cucina Enoteca | Nov 2021 – Apr 2023 | Last regular review; NYC health inspection of the next tenant |
| Samba Kitchen | ~Jan 2023 | Last regular review |
| K Rico Steakhouse | ~Aug 2023 | Local press (W42ST) |
| B Side Pizza & Wine Bar | Dec 2025 – Mar 2026 | Local press; next tenant opened in the space |

Each estimate has a lower and upper bound, a confidence level and its sources in `data/closed_restaurants.csv`. Closure dates are rarely announced, so the rule used is: **last review on the platform, confirmed by at least one outside source** (news, health inspections, a new business at the address).

## Platform quirks found along the way

- **TripAdvisor hides the reviews of closed restaurants.** None of the tested actors returned reviews for 4 of the 5 closed restaurants, even though the pages still show them. Closure is therefore analyzed on Yelp only. TripAdvisor is used for ranking and platform comparison on restaurants that are still open.
- **Listings get merged or moved.** TripAdvisor merged the two Spice Symphony locations into one listing, so that restaurant is excluded from the platform comparison. Murray's Cheese Bar's listings on both platforms were moved to its new Long Island City location. Reviews after 20 Aug 2020 are tagged separately (`location_period = murrays_lic`).
- **Reviewer stats are a snapshot.** Review counts, friends and similar values reflect the reviewer's profile on the collection date, not at the time the review was written.

## Repository structure

```
data/
  restaurants.csv          30 restaurants: Yelp URL, TripAdvisor ID, status
  closed_restaurants.csv   closure estimates, bounds and sources
  raw/                     raw actor output, JSON (not in git)
  clean/                   analysis tables, CSV (not in git)
src/
  01_scrape.py             runs the Apify actors (preflight / test / full)
  02_to_csv.py             raw JSON -> clean CSV tables
output/
  podesavanja_actora.md    exact actor settings and parameters (in Serbian)
```

The `clean/` step produces three tables:
- `yelp_reviews.csv`: one row per Yelp review (51,029 × 33)
- `tripadvisor_reviews.csv`: one row per TripAdvisor review (47,545 × 31)
- `restaurants.csv`: one row per restaurant with data from both platforms plus closure info (30 × 35)

**The review data is not in this repository** because it contains reviewer names and profile links. It was shared with the project mentors directly.

## Reproducing

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

1. Put your Apify token in a `.env` file: `APIFY_TOKEN=...`
2. Set `PLATFORM` and `MODE` at the top of `src/01_scrape.py`, then run it.
3. Run `src/02_to_csv.py` to build the CSV tables.

A full run of both platforms cost about $15 in Apify credits (Oct 2026 prices).

## Next steps

The mentors will build the composite ranking and validation. The planned design:
- Build the ranking from reviews up to **31 Dec 2021** and test it on what happened from **2022 onward**.
- A second cut at **end of 2019** puts all 30 restaurants and all 5 closures in the test, but it spans the pandemic.
- Robustness check: rank on 2022–2024, test on 2025–2026.

## Tech

Python 3.13 · pandas · numpy · scipy · matplotlib · apify-client
