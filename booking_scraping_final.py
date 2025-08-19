from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import csv, time, re

def handle(task, default=None):
    try:
        return task()
    except (NoSuchElementException, TimeoutException):
        return default

def first_number(text):
    if not text:
        return None
    m = re.search(r"[\d,.]+", text)
    return float(m.group(0).replace(",", "")) if m else None

# === Setup ===
CITIES = ['Aix en Provence', 'Avignon', 'Carcassonne', 'Grenoble', 'Toulouse'] 
BASE_URL = "https://www.booking.com/searchresults.html?ss={city}&nflt=ht_id=204"

driver = webdriver.Chrome(service=Service())
wait = WebDriverWait(driver, 12)
items = []

for city in CITIES:
    url = BASE_URL.format(city=city.replace(" ", "+"))
    print(f"🔍 Scraping city: {city}")
    driver.get(url)
    time.sleep(5)

    # Close sign-in / cookies if shown (best-effort)
    for sel in [
        "[role='dialog'] button[aria-label='Dismiss sign-in info.']",
        "#onetrust-accept-btn-handler",
        "[data-testid='accept-cookies-button']",
    ]:
        try:
            btn = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
            btn.click()
            time.sleep(0.2)
        except TimeoutException:
            pass

    hotels = driver.find_elements(By.CSS_SELECTOR, "[data-testid='property-card']")

    for hotel in hotels:
        hotel_url = handle(lambda: hotel.find_element(By.CSS_SELECTOR, "a[data-testid='title-link']").get_attribute("href"))
        name = handle(lambda: hotel.find_element(By.CSS_SELECTOR, "[data-testid='title']").text)
        address = handle(lambda: hotel.find_element(By.CSS_SELECTOR, "[data-testid='address']").text)
        distance = handle(lambda: hotel.find_element(By.CSS_SELECTOR, "[data-testid='distance']").text)
        rate = handle(lambda: hotel.find_element(By.CSS_SELECTOR, "[data-testid='review-score']").text)

        if not hotel_url:
            continue

        # Open hotel detail page in a new tab
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(hotel_url)
        time.sleep(2)

        # --- Description (your selector, then small fallbacks) ---
        full_description = handle(lambda: driver.find_element(By.CSS_SELECTOR, "p[data-testid='property-description']").text)
        if not full_description:
            full_description = handle(lambda: driver.find_element(By.CSS_SELECTOR, "div.c82435a4b8 p.a53cbfa6de.b3efd73f69").text)
        if not full_description:
            full_description = handle(lambda: driver.find_element(By.CSS_SELECTOR, ".a53cbfa6de.b3efd73f69").text)

        # --- Facilities (ul … li) with dedupe; fallback to older span selector ---
        fac_els = driver.find_elements(By.CSS_SELECTOR, "ul.e9f7361569.eb3a456445.b049f18dec li")
        if not fac_els:
            fac_els = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='property-most-popular-facilities-wrapper'] ul li span.a5a5a75131")
        seen, facilities_list = set(), []
        for el in fac_els:
            t = el.text.strip()
            if t and t not in seen:
                seen.add(t)
                facilities_list.append(t)

        # --- Number of reviews (your selector), then fallbacks ---
        num_reviews_text = handle(lambda: driver.find_element(By.CSS_SELECTOR, "div.fff1944c52.fb14de7f14.eaa8455879").text)
        if not num_reviews_text:
            # common fallbacks on detail page
            num_reviews_text = handle(lambda: driver.find_element(By.CSS_SELECTOR, "[data-testid='review-subtitle']").text)
        if not num_reviews_text:
            # older class-based blocks (sometimes multiple nodes; pick the 2nd when present)
            els = driver.find_elements(By.CSS_SELECTOR, ".a3b8729ab1.f45d8e4c32.d935416c47")
            if len(els) >= 2 and els[1].text.strip():
                num_reviews_text = els[1].text.strip()
            elif len(els) == 1 and els[0].text.strip():
                num_reviews_text = els[0].text.strip()
        num_reviews = first_number(num_reviews_text)

        # --- Lat/Long (unchanged) ---
        latlong = handle(lambda: driver.find_element(By.CSS_SELECTOR, "a[data-atlas-latlng]").get_attribute("data-atlas-latlng"))
        latitude = longitude = None
        if latlong and "," in latlong:
            try:
                lat_s, lon_s = latlong.split(",", 1)
                latitude = round(float(lat_s), 6)
                longitude = round(float(lon_s), 6)
            except ValueError:
                pass

        # close detail tab, go back
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        items.append({
            "City": city,
            "Hotel Name": name.strip() if name else None,
            "Rate": rate.strip() if rate else None,
            "Number of Reviews": num_reviews,
            "Neighborhood": address,
            "Distance from Center": distance,
            "Description": full_description.strip() if full_description else None,
            "Facilities": ", ".join(facilities_list) if facilities_list else None,
            "Address": address.strip() if address else None,
            "Latitude": latitude,
            "Longitude": longitude,
            "Hotel URL": hotel_url,
        })

    time.sleep(1)

# === Export to CSV ===
output_file = "booking_hotels_allcities_full.csv"
with open(output_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(items[0].keys()))
    writer.writeheader()
    writer.writerows(items)

print(f"✅ Scraping complete! {len(items)} hotels saved to {output_file}")
driver.quit()
