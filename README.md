# CDSD (Jedha) — Bloc 1 · Data Infrastructure · **Kayak / Booking**

> **One-liner:** Data Lake → Data Warehouse pipeline for Kayak’s “Best Destinations in France” prototype, mixing **weather** + **hotel** data and publishing interactive **maps**.

---

## 📇 Company
**Kayak** is a travel search engine (founded 2004 by Steve Hafner & Paul M. English), acquired by **Booking Holdings** (Booking.com, Kayak, Priceline, Agoda, RentalCars, OpenTable). With $300M+ yearly revenue, Kayak operates globally to help users plan trips at the best price.

---

## 🚧 Project
User research shows **70%** of Kayak users planning a trip want **more destination info**, but they distrust content from unknown brands.  
**Goal:** build an app that recommends where to go (and which hotels) using **real data** on:
- **Weather**
- **Hotels in the area**

The app should rank destinations/hotels “now” (rolling 7-day horizon).

---

## 🎯 Objectives
1. Scrape destination data  
2. Get **weather** for each destination  
3. Get **hotel** info for each destination  
4. Store raw/enriched data in a **Data Lake (S3)**  
5. **ETL** clean data from the lake to a **Data Warehouse (AWS RDS / SQL)**

---

## 🖼️ Scope — Cities (France)
Focus on **35** French destinations from OneWeekIn.com.

<details>
<summary>Show city list</summary>

Mont Saint Michel, St Malo, Bayeux, Le Havre, Rouen, Paris, Amiens, Lille, Strasbourg, Chateau du Haut Koenigsbourg, Colmar, Eguisheim, Besancon, Dijon, Annecy, Grenoble, Lyon, Gorges du Verdon, Bormes les Mimosas, Cassis, Marseille, Aix en Provence, Avignon, Uzes, Nimes, Aigues Mortes, Saintes Maries de la mer, Collioure, Carcassonne, Ariege, Toulouse, Montauban, Biarritz, Bayonne, La Rochelle
</details>

---

## 🦮 Data sources
- **Geocoding:** https://nominatim.org/ (no API key). Use `/search` to get **lat/lon** for each city.  
- **Weather:** https://openweathermap.org/api/one-call-api (free API key via https://openweathermap.org/appid). Pull 7-day daily metrics (`temp`, `pop`, `rain`, `humidity`, etc.).  
- **Hotels (Booking.com):** scrape for:
  - name
  - booking URL
  - latitude / longitude
  - user score
  - short description

> Use your own heuristics to score “nice weather” (e.g., low `pop` & `rain`, comfortable `temp`, moderate `humidity`). Save enriched results to **CSV**.

---

## 🗺️ Maps (preview)
Static screenshots for quick viewing on GitHub.  
Open the HTML demo or the notebook for full interactivity.

| Top 5 destinations | Top 20 hotels |
|---|---|
| ![Top 5](maps/Top5destinations.png) | ![Top 20](maps/top20hotels.png) |

**Interactive HTML:** `docs/hotel_map.html` (served via GitHub Pages)

---

## 🔄 Architecture (high level)
- **Ingest (Python/Colab):**
  - Cities → **Nominatim** (lat/lon)
  - Lat/lon → **OpenWeather One-Call** (7-day)
  - City → **Booking.com** scrape (hotels)
- **Data Lake (S3):** store raw CSVs
- **Warehouse (AWS RDS / Postgres or MySQL):**
  - create schema & tables
  - load cleaned, deduped, typed data (idempotent upserts)
- **Analytics:** Plotly maps → export **HTML** + **PNG**

---

## 📦 Deliverables
- `s3://.../france_destinations_enriched.csv` (weather + hotels + city_id)  
- **SQL Database** on AWS RDS containing the same cleaned data  
- Two maps:
  - **Top-5 destinations**
  - **Top-20 hotels** (by score/filters)

---
