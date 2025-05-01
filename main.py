# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# import time
# import random
# import json
# from pathlib import Path
#
#
# def zachowuj_sie_jak_czlowiek(driver):
#     body = driver.find_element(By.TAG_NAME, 'body')
#     for _ in range(2):
#         body.send_keys(Keys.PAGE_DOWN)
#         time.sleep(random.uniform(1.0, 2.5))
#
#
# def pobierz_produkty_z_wielu_stron(base_url, driver, max_stron=50):
#     wszystkie_produkty = []
#     page_number = 1
#
#     while page_number <= max_stron:
#         url = f"{base_url}?page={page_number}"
#         print(f"➡ Pobieram stronę {page_number}: {url}")
#         try:
#             driver.get(url)
#             time.sleep(random.uniform(3.0, 5.0))
#
#             zachowuj_sie_jak_czlowiek(driver)
#
#             produkty = driver.find_elements(By.CSS_SELECTOR, 'article.product--hasBadges')
#
#             if not produkty:
#                 print("❌ Brak produktów, koniec.")
#                 break
#
#             for prod in produkty:
#                 try:
#                     tytul = prod.find_element(By.CSS_SELECTOR, 'div.product__title').text.strip()
#                     cena = prod.find_element(By.CSS_SELECTOR, 'div[data-testid="product-price"]').text.strip()
#                     wszystkie_produkty.append({'nazwa': tytul, 'cena': cena})
#                 except:
#                     continue
#
#         except Exception as e:
#             print(f"❌ Błąd: {e}")
#             break
#
#         page_number += 1
#         time.sleep(random.uniform(2.0, 3.5))
#
#     return wszystkie_produkty
#
#
# def zapisz_do_json(nazwa_kategorii, dane):
#     Path("dane").mkdir(exist_ok=True)
#     nazwa_pliku = f"dane/{nazwa_kategorii.replace(' ', '_').lower()}.json"
#     with open(nazwa_pliku, "w", encoding="utf-8") as f:
#         json.dump(dane, f, ensure_ascii=False, indent=2)
#     print(f"💾 Zapisano do pliku: {nazwa_pliku}")
#
#
# def main():
#     options = uc.ChromeOptions()
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--disable-dev-shm-usage")
#
#     driver = uc.Chrome(options=options)
#
#     kategorie = {
#         # "Wyroby cukiernicze": "https://www.kaufland.pl/c/wyroby-cukiernicze/~69190/",
#         # "Słone przekąski": "https://www.kaufland.pl/c/slone-przekaski/~1581/",
#         # "Czekolady": "https://www.kaufland.pl/c/czekolady/~1431/",
#         "Mleko": "https://www.kaufland.pl/c/~1951/"
#     }
#
#     for nazwa_kategorii, url in kategorie.items():
#         print(f"\n{'=' * 40}\n📦 Kategoria: {nazwa_kategorii}\n{'=' * 40}")
#         produkty = pobierz_produkty_z_wielu_stron(url, driver)
#         if produkty:
#             zapisz_do_json(nazwa_kategorii, produkty)
#         else:
#             print("❌ Brak produktów lub odmowa dostępu.")
#
#     driver.quit()
#
#
# if __name__ == "__main__":
#     main()


import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import json
from pathlib import Path


def zamknij_cookies(driver):
    try:
        btn = driver.find_element(By.CSS_SELECTOR, 'button.cc__accept-btn')
        btn.click()
        print("✅ Zamknięto baner cookies (Kaufland)")
        time.sleep(2)
    except:
        print("ℹ️ Nie znaleziono banera cookies lub już zamknięty.")


def zachowuj_sie_jak_czlowiek(driver, scroll_times=12):
    for _ in range(scroll_times):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(random.uniform(0.5, 1.2))


def pobierz_produkty_z_aktualnej_strony(driver):
    produkty = []
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article.product--hasBadges"))
        )
        zachowuj_sie_jak_czlowiek(driver)
        artykuly = driver.find_elements(By.CSS_SELECTOR, "article.product--hasBadges")
        for prod in artykuly:
            try:
                nazwa = prod.find_element(By.CSS_SELECTOR, "div.product__title").text.strip()
                cena = prod.find_element(By.CSS_SELECTOR, "div[data-testid='product-price']").text.strip()
                produkty.append({'nazwa': nazwa, 'cena': cena})
            except:
                continue
    except:
        print("⚠️ Nie udało się pobrać produktów z tej strony.")
    return produkty


def kliknij_przycisk_dalej(driver):
    try:
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        przycisk_dalej = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.rd-page--arrow-btn:not([disabled])"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", przycisk_dalej)
        time.sleep(1)
        przycisk_dalej.click()
        print("➡️ Kliknięto przycisk 'Dalej'")
        return True
    except Exception as e:
        print(f"⛔ Nie znaleziono przycisku 'Dalej' – to była ostatnia strona. ({e})")
        return False



def zapisz_do_json(nazwa_pliku, dane):
    Path("dane").mkdir(exist_ok=True)
    sciezka = f"dane/{nazwa_pliku}.json"
    with open(sciezka, "w", encoding="utf-8") as f:
        json.dump(dane, f, ensure_ascii=False, indent=2)
    print(f"💾 Dane zapisane do pliku: {sciezka}")


def main():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options, headless=False, use_subprocess=True)

    url = "https://www.kaufland.pl/c/~1951/"
    driver.get(url)
    zamknij_cookies(driver)
    time.sleep(4)

    wszystkie_produkty = []
    numer_strony = 1

    while True:
        print(f"\n📄 Pobieram stronę {numer_strony}")
        produkty = pobierz_produkty_z_aktualnej_strony(driver)
        print(f"🔍 Znaleziono {len(produkty)} produktów")
        wszystkie_produkty.extend(produkty)

        if not kliknij_przycisk_dalej(driver):
            break

        numer_strony += 1
        time.sleep(random.uniform(3.0, 5.0))

    zapisz_do_json("mleko_kaufland", wszystkie_produkty)
    driver.quit()


if __name__ == "__main__":
    main()

