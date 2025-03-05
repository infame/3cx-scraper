from pathlib import Path
from bs4 import BeautifulSoup

# Файл HTML-кэша
cache_file = Path("html_cache/AE_RK_.html")

# Проверяем, существует ли файл
if not cache_file.exists():
    print(f"Файл {cache_file} не найден!")
    exit(1)

# Читаем содержимое файла
with cache_file.open("r", encoding="utf-8") as file:
    html_content = file.read()

# Разбираем HTML с помощью BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Выводим заголовки уровней партнёров
h3_tags = soup.find_all("h3")
for h3 in h3_tags:
    print(f"Partner Level: {h3.get_text(' ', strip=True)}")

# Ищем все карточки партнёров
partner_boxes = soup.find_all("div", class_="xcx_partner_box")

for box in partner_boxes:
    # Имя компании
    company_name_elem = box.find("a")
    company_name = company_name_elem.find("strong").get_text(strip=True) if company_name_elem else "Unknown"

    # Извлекаем flex-блоки (div с inline стилем "display:flex")
    flex_divs = box.find_all("div", style=lambda value: value and "display:flex" in value)

    if len(flex_divs) >= 4:
        # Первый flex-блок: телефон
        telephone = flex_divs[0].get_text(strip=True)
        # Второй flex-блок: веб-сайт
        website = flex_divs[1].get_text(strip=True)
        # Третий flex-блок: адрес
        address = flex_divs[2].get_text(strip=True)
        # Четвёртый flex-блок: Partner ID (удаляем лишнее)
        partner_id_text = flex_divs[3].get_text(strip=True)
        partner_id = partner_id_text.replace("Partner ID:", "").strip()
    else:
        telephone = website = address = partner_id = "N/A"

    print(f"""
    Company: {company_name}
    Telephone: {telephone}
    Website: {website}
    Address: {address}
    Partner ID: {partner_id}
    """)

print("Парсинг завершён!")