from config import settings
from datetime import datetime
from typing import Any
import asyncio
import aiohttp
import re



URL = settings.MARKET_API_URL
TOKEN = settings.MARKET_API_TOKEN
PERCENT = settings.PERCENT_OF_SELLER*0.01


async def extract_ids(links: list[str]) -> list[int]:
    pattern = re.compile(r"(?:https?://)?lzt\.market/([^/]+)")
    ids: list[int] = []

    for link in links:
        if link.isdigit():
            ids.append(int(link))
        else:
            match = pattern.search(link)
            if match:
                ids.append(int(match.group(1)))
            else:
                print(f"Ошибка в ссылке: {link}")
    return ids


async def fetch_data(session: aiohttp.ClientSession, id: int) -> Any:
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {TOKEN}"
    }
    
    async with session.get(f"{URL}{id}", headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Ошибка с {id}")
            return None


async def create_report(links):
    ids = await extract_ids(links)
    
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
    failed_accounts: list[str] = []

    async with aiohttp.ClientSession() as session:
        for id in ids:
            accounts_count += 1
            
            response = await fetch_data(session, id)
            if response is not None:
                try:
                    item = response["item"]
                    title: str = item["title"]
                    price: int = int(float(item["price"]))
                    price_after_comission = price*0.97
                    share_from_price = price*0.97*PERCENT
                    
                    summ_after_commission += price_after_comission
                    summ_share_from_price += share_from_price

                    info: str = f"https://lzt.market/{id} // Цена после коммиссии: {price_after_comission:.2f} // Доля: {share_from_price:.2f} // {title}"

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
                    await asyncio.sleep(0.2)

                except:
                    failed_accounts.append("https://lzt.market/{id}")
                    print(f"Произошла ошибка при проверке: https://lzt.market/{id}")
        
        # REPORT OUTPUT START
        output_sold_accounts = "\n".join(sold_accounts)
        output_not_sold_accounts = "\n".join(not_sold_accounts)
        output_failed_accounts = "\n".join(failed_accounts)

        output: str = f"""ОТЧЕТ {datetime.now()}

- Всего аккаунтов: {accounts_count} | Сумма: {summ_after_commission:.2f} | Доля: {summ_share_from_price:.2f} | Скока скинуть: {summ_after_commission-summ_share_from_price:.2f}
- Продано аккаунтов: {sold_accounts_count} | Сумма: {summ_sold_accounts:.2f} | Доля: {summ_share_sold_accounts:.2f} | Скока скинуть: {summ_sold_accounts-summ_share_sold_accounts:.2f}
- Не продано аккаунтов: {not_sold_accounts_count} | Сумма: {summ_not_sold_accounts:.2f} | Доля: {summ_share_not_sold_accounts:.2f} | Скока скинуть: {summ_not_sold_accounts-summ_share_not_sold_accounts:.2f}

ПРОДАННЫЕ:
{output_sold_accounts}

НЕПРОДАННЫЕ:
{output_not_sold_accounts}

НЕПРОВЕРЕННЫЕ(ОШИБКИ):
{output_failed_accounts}
"""
        
        return output