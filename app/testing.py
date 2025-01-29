from selenium import webdriver
from selenium.webdriver.common.by import By



def scraping_using_selenium():
    """
    Retrieve information using Selenium.

    Returns:
        None
    """
    driver = webdriver.Chrome()
    for i in range(10):
        driver.get(f"https://www.luxor.cz/c/9548/knihy?pi={i + 1}")
        books = [book.find_element(By.CLASS_NAME, "product-box").find_element(By.CLASS_NAME, "product-box__title").get_attribute("href") for book in
                 driver.find_element(By.CLASS_NAME, "product-list").find_elements(By.TAG_NAME, "cmp-product-box")]
        for book in books:
            detaily = {}
            driver.get(book)
            title = driver.find_element(By.TAG_NAME, "h1").text
            details = driver.find_elements(By.XPATH, ".//div[@class='detail-info__item']")
            for detail in details:
                detaily[detail.split(":")[0]] = detail.split(":")[1].strip()
scraping_using_selenium()

