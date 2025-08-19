# Kayak / Booking — CDSD (Jedha) · Bloc 1 · Data Infrastructure

**Goal:** Build the data foundation for a **destination & hotel recommendation** prototype using **real weather** + **hotel** data, delivered via a **Data Lake → Warehouse** pipeline and **interactive maps**.

---

## Live
- 🗺️ **Destinations (HTML):** https://sonydata.github.io/cdsd-jedha-2025-b01-data-infra-kayak/top5destinations_final.html  
- 🏨 **Hotels (HTML):** https://sonydata.github.io/cdsd-jedha-2025-b01-data-infra-kayak/top_hotels_5cities_layers.html  
- 📓 **Colab (maps only):** [Open in Colab](https://colab.research.google.com/drive/107LhXhZRFf22gu39KB2NhP3dPIQyRocl?usp=sharing)

**Previews (click):**  
[![Destinations](maps/Top5destinations.png)](https://sonydata.github.io/cdsd-jedha-2025-b01-data-infra-kayak/top5destinations_final.html)
[![Hotels](maps/top20hotels_copy.png)](https://sonydata.github.io/cdsd-jedha-2025-b01-data-infra-kayak/top_hotels_5cities_layers.html)

---

## Project (context)
- **User research:** ~**70%** of planners want **more destination information** and trust content from known brands.  
- **Objective:** enable an application that can recommend **where to go next** and **which hotels to consider**, based on **current weather** and **nearby hotels**.  
- **This repo (Phase 1):** collect data, land in a **data lake**, **clean/transform**, load into a **warehouse**, and ship **interactive map prototypes**.

## Goals
- Scrape data from **destinations**.  
- Get **weather** data for each destination.  
- Get **hotel** info for each destination.  
- Store everything in a **data lake (S3)**.  
- **Extract, Transform, Load** cleaned data from the lake into a **data warehouse (AWS RDS)**.

---

## Pipeline
Acquire → Clean / Transform → Load (Warehouse) → Prototype Maps
Nominatim, OpenWeather, Booking └─ City_ID join, types └─ staged load + upserts └─ Plotly/Folium HTML+PNG

---

## Steps & key files
| Path | Purpose | Output |
|---|---|---|
| `Weather_data_API.ipynb` | Geocode cities (Nominatim) + fetch 7-day weather (OpenWeather) | `files for S3/Weather-data-sorted-*.csv` |
| `booking_scraping_final.py` | Booking.com scrape (name, URL, coords, rating, reviews, amenities, distance) | `hotels_clean.csv` |
| `SQLAlchemy.ipynb` | Clean + merge on `City_ID` → staged load + **idempotent upserts** to RDS | optional export: `clean_hotel_weather_data_RDS.csv` |
| `docs/top5destinations.html` | Destination map prototype (GitHub Pages) | preview: `maps/Top5destinations.png` |
| `docs/top20hotels-v2.html` | Hotels map prototype (GitHub Pages) | preview: `maps/top20hotels.png` |
| `files for S3/` | Lake-ready CSVs | enriched weather + hotels + `city_id` |
| `S3bucket_content.png` | Data Lake proof | screenshot |

**Core transforms:** `Rate→float`, `Number of Reviews→int`, tidy column names; weather `dt→Date`; `INNER JOIN` on `City_ID`; drop duplicate geo columns; rename (`Date→Weather_Date`, `Min/Max→*_Temp`); put `City_ID` first.  
**Weather rule of thumb (prototype):** `avg_max_temp>10 °C`, `rain_prob≤0.25`, `avg_clouds<55%`, `wind<7 m/s`.

---

## Data sources
- **Geocoding:** Nominatim `/search` → `lat/lon` (no key).  
- **Weather:** OpenWeather **One-Call** (7-day daily: `temp`, `pop`, `rain`, `humidity`, `clouds`, `wind`).  
- **Hotels (Booking.com):** name, URL, coordinates, rating, reviews, amenities, distance from center.  
  *Educational scraping only (polite headers, throttling).*

---

## Tools
Python 3.10+, pandas, numpy, requests, **plotly**, **folium**, SQLAlchemy · AWS **S3**/**RDS** · Nominatim, OpenWeather · `.env`
