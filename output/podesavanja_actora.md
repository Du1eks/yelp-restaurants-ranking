# Prilog: podešavanja Apify actora za preuzimanje recenzija

Podaci su preuzeti preko platforme Apify (apify.com) 19. 10. 2026. Ulaz su 30 restorana iz rada iz 2019. godine,
redosledom iz tog rada (restaurant_id 1–30). Za obe platforme preuzete su **sve recenzije od otvaranja restorana,
na svim jezicima, bez vremenskog ograničenja i bez limita po restoranu**. Sirovi rezultat je sačuvan kao JSON,
a CSV tabele su napravljene iz njega skriptom `src/02_to_csv.py`.

## 1. Yelp

| | |
|---|---|
| Actor | `epicscrapers/yelp-reviews-scraper` (https://apify.com/epicscrapers/yelp-reviews-scraper), build 0.0.6 |
| Run | `ismNI9htE9CR1Fd35`, 19. 10. 2026, 13:06–13:14 UTC |
| Restorana | 30 |
| Recenzija | 51.029 (Yelp prikazuje 51.005; razlika 0 do +4 po restoranu = nove recenzije tokom preuzimanja) |
| Cena | $0,25 / 1.000 recenzija; ukupno $12,76 |
| Sirov fajl | `data/raw/yelp_full.json` |

Ulazni parametri:
```json
{
  "businesses": [
    "https://www.yelp.com/biz/piccola-cucina-osteria-new-york",
    "https://www.yelp.com/biz/piccola-cucina-enoteca-new-york-2",
    "https://www.yelp.com/biz/club-a-steakhouse-new-york",
    "https://www.yelp.com/biz/sottocasa-pizzeria-harlem-new-york",
    "https://www.yelp.com/biz/boucherie-union-square-new-york",
    "https://www.yelp.com/biz/loi-estiatorio-new-york",
    "https://www.yelp.com/biz/song-e-napule-new-york",
    "https://www.yelp.com/biz/los-tacos-no-1-new-york-3",
    "https://www.yelp.com/biz/boucherie-west-village-new-york-3",
    "https://www.yelp.com/biz/petite-boucherie-new-york",
    "https://www.yelp.com/biz/daniel-new-york-4",
    "https://www.yelp.com/biz/olio-e-pi%C3%BA-new-york-3",
    "https://www.yelp.com/biz/spice-symphony-new-york",
    "https://www.yelp.com/biz/spice-symphony-new-york-3",
    "https://www.yelp.com/biz/sottocasa-pizzeria-brooklyn-3",
    "https://www.yelp.com/biz/le-bernardin-new-york",
    "https://www.yelp.com/biz/royal-35-steakhouse-new-york",
    "https://www.yelp.com/biz/murrays-cheese-bar-new-york",
    "https://www.yelp.com/biz/pure-thai-cookhouse-new-york",
    "https://www.yelp.com/biz/k-rico-steakhouse-new-york",
    "https://www.yelp.com/biz/jungsik-new-york",
    "https://www.yelp.com/biz/samba-kitchen-new-york-5",
    "https://www.yelp.com/biz/b-side-pizza-and-wine-bar-new-york",
    "https://www.yelp.com/biz/san-carlo-osteria-piemonte-new-york-city",
    "https://www.yelp.com/biz/per-se-new-york",
    "https://www.yelp.com/biz/the-modern-new-york-3",
    "https://www.yelp.com/biz/gabriel-kreuther-new-york",
    "https://www.yelp.com/biz/eileens-special-cheesecake-new-york",
    "https://www.yelp.com/biz/julianas-pizza-brooklyn-5",
    "https://www.yelp.com/biz/russ-and-daughters-new-york"
  ],
  "maxReviewsPerBusiness": 0,
  "sortBy": "newest",
  "languages": [],
  "includeReviewerDetails": true
}
```

## 2. TripAdvisor

| | |
|---|---|
| Actor | `kaix/tripadvisor-reviews-scraper` (https://apify.com/kaix/tripadvisor-reviews-scraper), build 0.2.46 |
| Run | `RbxNSbOsWUVAjS00k`, 19. 10. 2026, 12:45–12:53 UTC |
| Restorana | 29 traženo (bez r13), 25 sa recenzijama |
| Recenzija | 47.545 |
| Cena | $0,05 / 1.000 recenzija; ukupno $2,38 |
| Sirov fajl | `data/raw/tripadvisor_full.json` |

Ulazni parametri (TripAdvisor `locationId`, redosled restaurant_id bez 13):
```json
{
  "businesses": [
    "4363835",
    "1731141",
    "1236281",
    "10165896",
    "13504265",
    "7814915",
    "8319600",
    "4578404",
    "11918545",
    "10145683",
    "457808",
    "1878682",
    "3603515",
    "3437996",
    "424434",
    "12015308",
    "4888905",
    "2099173",
    "7617787",
    "2345886",
    "10781002",
    "7078660",
    "10032108",
    "425628",
    "549201",
    "8483826",
    "808386",
    "3741802",
    "1224238"
  ],
  "maxReviews": 0,
  "language": "all"
}
```

## 3. Napomene

- **Izbor actora.** U radu iz 2026. (Filip) navedeni su samo ulazni parametri, ne i imena actora. Izabrani su actori koji
  vraćaju sva tražena polja. Za Yelp je provereno da `epicscrapers` vraća iste recenzije kao drugi actori (20/20 istih ID-jeva
  i ID-jeva recenzenata kao `tri_angle/yelp-review-scraper`). Provera na 2 restorana po platformi: broj preuzetih recenzija
  jednak je broju prikazanom na stranici (Yelp 316/316, 956/955; TripAdvisor 3.577/3.577, 643/644).
- **Polja koja nedostaju.** Yelp: datum odgovora vlasnika (tekst i uloga autora postoje). TripAdvisor: helpful glasovi
  recenzenta sa profila (sačuvani su korisničko ime i link profila radi kasnije dopune). Nijedan actor ne vraća
  „claimed” status ni nagrade.
- **Zatvoreni restorani na TripAdvisor-u.** Za Piccola Cucina Enoteca, Murray's Cheese Bar, K Rico i Samba Kitchen nijedan
  actor ne vraća recenzije (za K Rico probana tri actora: kaix, thewolves, maxcopell), iako stranica u browser-u prikazuje
  recenzije. Jedini zatvoreni sa TripAdvisor podacima je B Side (TripAdvisor ga nije označio kao zatvorenog).
- **Spice Symphony.** TripAdvisor je spojio lokacije na Lexingtonu (r13) i 50th St (r14) u jedan listing (3603515);
  r13 nema TripAdvisor podatke, a r14 se ne koristi u poređenju platformi.
- **Murray's Cheese Bar.** Yelp listing je prebačen sa Bleecker St na novi lokal u Long Island City; recenzije od
  20. 8. 2020. označene su u `yelp_reviews.csv` kao `location_period = murrays_lic`.
- **Vrednosti o recenzentu** (broj recenzija/doprinosa, prijatelja, fotografija, Elite) su stanje profila na dan preuzimanja,
  ne u trenutku pisanja recenzije.
- **Datumi.** Yelp: datum i vreme u UTC. TripAdvisor: datum objave (bez vremena) i mesec posete.
