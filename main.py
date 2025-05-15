import time
import random
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains



try:
    from selenium_stealth import stealth
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False
    print("⚠️ selenium_stealth nie jest zainstalowany. Funkcja stealth będzie pominięta.")

def zamknij_cookies(driver):
    print('🟡 Sprawdzam obecność banera cookies...')
    try:
        time.sleep(random.uniform(1.0, 2.5))  # czas na pojawienie się banera
        
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button#onetrust-accept-btn-handler'))
        )
        
        actions = ActionChains(driver)
        actions.move_to_element(btn).pause(random.uniform(0.4, 1.0)).click().perform()
        
        print("✅ Zamknięto baner cookies (Kaufland)")
        time.sleep(random.uniform(1.0, 2.0))
    except Exception as e:
        print(f"ℹ️ Baner cookies nie pojawił się lub już zamknięty. ({e})")

def zachowuj_sie_jak_czlowiek(driver, scroll_times=8):
    for _ in range(scroll_times):
        scroll_amount = random.randint(500, 800)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.7, 1.5))

def pobierz_produkty_z_aktualnej_strony(driver):
    produkty = []
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article.product")))
        zachowuj_sie_jak_czlowiek(driver)

        artykuly = driver.find_elements(By.CSS_SELECTOR, "article.product")
        for prod in artykuly:
            try:
                nazwa = prod.find_element(By.CSS_SELECTOR, "div.product__title").text.strip()
                cena = prod.find_element(By.CSS_SELECTOR, "div[data-testid='product-price']").text.strip()
                produkty.append({'nazwa': nazwa, 'cena': cena})
                print(produkty[-1])
            except Exception as e:
                print(f"⚠️ Błąd przy parsowaniu produktu: {e}")
                continue
    except Exception as e:
        print(f"⚠️ Nie udało się pobrać produktów: {e}")
    return produkty

def kliknij_przycisk_dalej(driver):
    try:
        # Pobierz aktualny URL przed kliknięciem
        current_url = driver.current_url
        
        # Znajdź i kliknij przycisk przez JavaScript (mniej wykrywalne)
        przycisk = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.rd-page--arrow-btn[aria-hidden='false']")))
        
        driver.execute_script("""
            arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});
            setTimeout(function() {
                arguments[0].click();
            }, 1500);
        """, przycisk)
        
        # Czekaj na zmianę URL (ale nie za krótko)
        time.sleep(random.uniform(3.0, 5.0))
        
        # Ręczne odświeżenie strony jeśli zawartość się nie zmieniła
        if driver.current_url == current_url:
            print("⚠️ Zawartość się nie załadowała, próbuję odświeżyć...")
            driver.refresh()
            time.sleep(random.uniform(2.0, 4.0))
            
        # Dodatkowe zabezpieczenie - symuluj ludzkie zachowanie
        actions = ActionChains(driver)
        actions.move_by_offset(random.randint(1, 10), random.randint(1, 10)).perform()
        
        return True
        
    except Exception as e:
        print(f"⛔ Błąd przy zmianie strony: {str(e)}")
        return False
    
def zapisz_do_json(nazwa_pliku, dane):
    Path("dane").mkdir(exist_ok=True)
    sciezka = f"dane/{nazwa_pliku}.json"
    with open(sciezka, "w", encoding="utf-8") as f:
        json.dump(dane, f, ensure_ascii=False, indent=2)
    print(f"💾 Zapisano {len(dane)} produktów do: {sciezka}")

def main():
    # Konfiguracja opcji Chrome
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    
    # Pobierz i ustaw ChromeDriver za pomocą webdriver_manager
    service = Service(ChromeDriverManager().install())
    
    # Inicjalizacja WebDrivera
    driver = webdriver.Chrome(service=service, options=options)
    
    # Zastosuj stealth tylko jeśli biblioteka jest dostępna
    if STEALTH_AVAILABLE:
        stealth(driver,
               languages=["en-US", "en"],
               vendor="Google Inc.",
               platform="MacIntel",
               webgl_vendor="Intel Inc.",
               renderer="Intel Iris OpenGL Engine",
               fix_hairline=True)
    else:
        print("⚠️ Pomijam konfigurację stealth - brak wymaganej biblioteki.")

    try:
        url = "https://www.kaufland.pl/c/~1951/?page=1"
        driver.get(url)
        zamknij_cookies(driver)
        time.sleep(3)

        wszystkie_produkty = []
        numer_strony = 1
        max_stron = int(driver.find_element(By.CSS_SELECTOR,"nav.search-pagination button:nth-last-child(2)").text)
        nastepna_strona = numer_strony + 1
        print("MAX STRON:", max_stron)
        while numer_strony <= max_stron:
            print(f"\n📄 Strona {numer_strony}/{max_stron}")
            produkty = pobierz_produkty_z_aktualnej_strony(driver)
            print(f"🔍 Znaleziono: {len(produkty)} produktów")
            
            wszystkie_produkty.extend(produkty)
            
            if not kliknij_przycisk_dalej(driver):
                break
            numer_strony += 1
            time.sleep(random.uniform(3.0, 6.0))

        zapisz_do_json("mleko_kaufland", wszystkie_produkty)
        
    except Exception as e:
        print(f"🚨 Krytyczny błąd: {e}")
    finally:
        driver.quit()
        print("🛑 Zakończono przetwarzanie")

if __name__ == "__main__":
    main()