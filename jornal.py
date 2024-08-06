from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
import time
import re
import pandas as pd

WINDOW_SIZE = "1920,1080"

chrome_options = Options()
#chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)

driver = webdriver.Edge(chrome_options)
driver.get('https://www.latimes.com/')
driver.maximize_window()

# First Page, open the Search bar and send the text
xpath_pesquisa = '/html/body/ps-header/header/div[2]/button'
xpath_search = '/html/body/ps-header/header/div[2]/div[2]/form/label/input'

# Everything that I will use
class_title = 'promo-title'
class_date = 'promo-timestamp'
class_description = 'promo-description'
class_image = 'image'

search_phrase = 'Olympics'

try:
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, xpath_pesquisa))
    ).click()
finally:
    print('cliquei')

try:
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, xpath_search))
    )
finally:
    element.send_keys(search_phrase)
    element.send_keys(Keys.RETURN)
    print('Enter pressed')

# Starts the news reading
articles = driver.find_elements(By.XPATH, '//ul[@class="search-results-module-results-menu"]/li')

first_article_date = None
if articles:
    first_article_date = articles[0].find_element(By.CLASS_NAME, class_date).text
    print(f"First article date: {first_article_date}")

# Prepare data storage
data = []

for article in articles:
    try:
        title = article.find_element(By.CLASS_NAME, class_title).text
        description = article.find_element(By.CLASS_NAME, class_description).text
        date = article.find_element(By.CLASS_NAME, class_date).text

        # Only process articles that have the same date as the first article
        if date != first_article_date:
            continue

        # Get image link and image name
        img = article.find_element(By.CLASS_NAME, class_image)
        image_url = img.get_attribute('src')
        image_alt = img.get_attribute('alt')

        count_phrases = title.lower().count(search_phrase.lower()) + description.lower().count(search_phrase.lower())

        # Check if the title or description contains any amount of money
        money_pattern = r'(\$\d+(?:,\d{3})*(?:\.\d+)?|\d+(?:,\d{3})*\s*(?:dollars|USD))'
        contains_money = bool(re.search(money_pattern, title + description))
    except Exception as e:
        print(f"Fail with: {e}")
        continue
    
    print(title)
    print(description)
    print(date)
    print(image_alt)
    img.screenshot(f"{title}.png")
    print(f"{search_phrase}: {count_phrases}")
    print(f"{contains_money}")

    # Store the data
    data.append({
        'title': title,
        'date': date,
        'description': description,
        'image': f"{title}.png",
        'image_alt': image_alt,
        'count_phrases': count_phrases,
        'contains_money': contains_money
    })

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel('latimes_olympics_news.xlsx', index=False)

# Close the WebDriver
driver.quit()