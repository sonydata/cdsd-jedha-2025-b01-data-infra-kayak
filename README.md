# CDSD (Jedha) — Bloc 1 · Data Infrastructure · Kayak / Booking

Data Lake → Data Warehouse pipeline that ranks **French destinations** using **7-day weather** + **hotel** data, with **interactive maps** (Plotly/Folium).

---

## 🚀 Quick demo
- 🗺️ **Top 5 Destinations (HTML)** — GitHub Pages  
  https://sonydata.github.io/cdsd-jedha-2025-b01-p01-data-infra-kayak/top5destinations.html
- 🏨 **Top 20 Hotels (HTML)** — GitHub Pages  
  https://sonydata.github.io/cdsd-jedha-2025-b01-p01-data-infra-kayak/top20hotels-v2.html
- 📓 **Colab notebook (maps only)**  
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/107LhXhZRFf22gu39KB2NhP3dPIQyRocl?usp=sharing)

| Top 5 destinations | Top 20 hotels |
|---|---|
| ![Top 5](maps/Top5destinations.png) | ![Top 20](maps/top20hotels.png) |

---

## 📄 Project description
Goal: centralize, clean, and merge **weather** (OpenWeather) and **hotel** (Booking.com) data to produce:
- a **Top-5** of cities for the next 7 days,
- a global **Top-20** of hotels,
- **CSV outputs** for the Data Lake (S3) and a **clean SQL table** (RDS).

**Weather heuristics** used to pick “nice weather” cities:  
`avg_max_temp > 10°C`, `rain_prob ≤ 0.25`, `avg_clouds < 55%`, `wind < 7 m/s`.

---

## 🧱 Architecture
1) **Acquisition** → Cities → Nominatim (lat/lon) → OpenWeather (daily 7-day) + Booking scraping (hotels).  
2) **Data Lake (S3)** → store raw & enriched CSVs.  
3) **ETL → DWH (AWS RDS)** → schema/type normalization, field validation & selection, enrichment via `City_ID`, **idempotent upserts**.  
4) **Analytics / Viz** → Plotly & Folium → export **HTML** (GitHub Pages) + **PNG**.

---

## 🔌 Data sources
- **Geocoding:** Nominatim `/search` → `lat/lon` (no API key).
- **Weather:** OpenWeather **One-Call** (7-day daily: `temp`, `pop`, `rain`, `humidity`, `clouds`, `wind`).
- **Hotels (Booking.com):** name, URL, coordinates, rating, reviews, **amenities** (équipements & services), distance from center, etc.  
  _Educational scraping only (polite headers, rate limiting)._

---

## 🧹 Key transformations (pre-DWH)
- **Hotels:** extract numeric `Rate → float`, cast `Number of Reviews → int`, standardize column names.  
- **Weather:** parse `dt → Date`, keep relevant metrics, normalize names (`ID`, `UVI`, Title_Case_With_Underscores).  
- **Merge:** `INNER JOIN` on `City_ID` → drop duplicate geo cols, rename leftovers (`Date→Weather_Date`, `Min/Max→*_Temp`), place `City_ID` first.

---

## 🗂️ Folders & key files

### Folders
- [`docs/`](./docs/) — HTML maps published via GitHub Pages (e.g., `top5destinations.html`, `top20hotels-v2.html`).
- [`maps/`](./maps/) — PNG previews used in the README.
- [`files for S3/`](./files%20for%20S3/) — CSVs ready for the Data Lake.

### Files (repo root)
| File | What it does | Output / Notes |
|---|---|---|
| `Weather_data_API.ipynb` | Weather collection (OpenWeather) + city geocoding (Nominatim). | Produces `Weather-data-sorted-3feb25*.csv`. |
| `booking_scraping_final.py` | Booking.com scraping: hotel name/URL/coords, rating, review count, amenities, distance. | Produces `hotels_clean.csv`. |
| `SQLAlchemy.ipynb` | ETL to **RDS**: cleaning, typing, weather+hotel merge via `City_ID`, staged load + upsert. | Optional export: `hotel_weather_clean_data.csv`. |
| `S3bucket_content.png` | Evidence of S3 Data Lake contents. | Screenshot. |
| `README.md` | This document. | — |

---

## 📦 Deliverables
- **Data Lake (S3):** enriched weather + hotels + `city_id` → [`files for S3/`](./files%20for%20S3/)  
  ![S3](S3bucket_content.png)
- **DWH (RDS):** cleaned, merged table (see `SQLAlchemy.ipynb`; `hotel_weather_clean_data.csv`).  
- **Maps:** HTML + PNG (links at the top).

---

## 🛠️ Stack & APIs
**Python 3.10+**, Pandas, NumPy, Requests, **Folium** / **Plotly**, SQLAlchemy,  
OpenWeather One-Call, Nominatim (OSM), AWS S3 / RDS, `.env` for secrets.

 
