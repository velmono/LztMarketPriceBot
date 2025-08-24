from datetime import datetime
from config import settings
import requests
import time
import re


URL = settings.MARKET_API_URL
TOKEN = settings.MARKET_API_TOKEN
PERCENT = settings.PERCENT_OF_SELLER*0.01

headers = {
    "accept": "application/json",
    "authorization": f"Bearer {TOKEN}"
}


try:
    with open("links.txt", "r") as file:
        links = file.readlines()
except FileNotFoundError as e:
    print(f"Create links.txt and fill with the links (link by line)")
    raise e


ids: list[int] = []

pattern = re.compile(r"(?:https?://)?lzt\.market/([^/]+)")

for link in links:
    match = pattern.search(link)
    if match:
        ids.append(int(match.group(1)))
    else:
        print(f"Ошибка в ссылке: {link}")


accounts_count: int = 0                     # Accounts counter
sold_accounts_count: int = 0                # Sold accounts counter
not_sold_accounts_count: int = 0            # Unsold accounts counter
summ_after_commission: float = 0            # Sum with market comission
summ_share_from_price: float = 0            # Seller's share

sold_accounts: list[str] = []               # Sold accounts
not_sold_accounts: list[str] = []           # Unsold accounts
summ_sold_accounts: float = 0               # Sold accounts sum 
summ_not_sold_accounts: float = 0           # Unsold accounts sum
summ_share_sold_accounts: float = 0         # Seller's share from accounts sold
summ_share_not_sold_accounts: float = 0     # Seller's share from accounts unsold



for id in ids:
    
    accounts_count += 1
    response = requests.get(url=f"{URL}{id}", headers=headers).json()
    
    try:
        item = response["item"]
        title: str = item["title"]
        price: int = int(float(item["price"]))
        price_after_comission = price*0.97
        share_from_price = price*0.97*PERCENT
        
        summ_after_commission += price_after_comission
        summ_share_from_price += share_from_price

        info: str = f"https://lzt.market/{id} // Цена после коммиссии: {price_after_comission:.2f} // Доля: {share_from_price:.2f} // {title}\n"

        if response["canBuyItem"] == True:
            not_sold_accounts_count += 1
            summ_not_sold_accounts += price_after_comission
            summ_share_not_sold_accounts += share_from_price
            not_sold_accounts.append(info)
        else:
            sold_accounts_count += 1
            summ_sold_accounts += price_after_comission
            summ_share_sold_accounts += share_from_price
            sold_accounts.append(info)

        # Rate limit (https://lzt-market.readme.io/reference/information#rate-limit)
        time.sleep(0.2)

    except:
        print(f"Произошла ошибка при проверке: https://lzt.market/{id}")



# REPORT OUTPUT START
output_sold_accounts = "".join(sold_accounts)
output_not_sold_accounts = "".join(not_sold_accounts)

output: str = f"""ОТЧЕТ {datetime.now()}

- Всего аккаунтов: {accounts_count} | Сумма: {summ_after_commission:.2f} | Доля: {summ_share_from_price:.2f} | Скока скинуть: {summ_after_commission-summ_share_from_price:.2f}
- Продано аккаунтов: {sold_accounts_count} | Сумма: {summ_sold_accounts:.2f} | Доля: {summ_share_sold_accounts:.2f} | Скока скинуть: {summ_sold_accounts-summ_share_sold_accounts:.2f}
- Не продано аккаунтов: {not_sold_accounts_count} | Сумма: {summ_not_sold_accounts:.2f} | Доля: {summ_share_not_sold_accounts:.2f} | Скока скинуть: {summ_not_sold_accounts-summ_share_not_sold_accounts:.2f}

ПРОДАННЫЕ:
{output_sold_accounts}

НЕПРОДАННЫЕ:
{output_not_sold_accounts}


"""

# WRITING REPORT IN THE FILE
with open(file="output.txt", mode="w", encoding="utf-8") as file:
    file.write(output)
# REPORT OUTPUT END