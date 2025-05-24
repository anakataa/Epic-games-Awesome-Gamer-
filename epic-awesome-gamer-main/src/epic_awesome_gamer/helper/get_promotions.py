from __future__ import annotations

from contextlib import suppress
from json import JSONDecodeError
from typing import List

import httpx
from loguru import logger

from epic_awesome_gamer.types import PromotionGame

URL_PROMOTIONS = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
URL_PRODUCT_PAGE = "https://store.epicgames.com/en-US/p/"
URL_PRODUCT_BUNDLES = "https://store.epicgames.com/en-US/bundles/"


def get_promotions() -> List[PromotionGame]:
  
    def is_discount_game(prot: dict) -> bool | None:
        with suppress(KeyError, IndexError, TypeError):
            offers = prot["promotions"]["promotionalOffers"][0]["promotionalOffers"]
            for i, offer in enumerate(offers):
                if offer["discountSetting"]["discountPercentage"] == 0:
                    return True

    promotions: List[PromotionGame] = []

    resp = httpx.get(URL_PROMOTIONS, params={"local": "zh-CN"})

    try:
        data = resp.json()
    except JSONDecodeError as err:
        logger.error("Failed to get promotions", err=err)
        return []

    # Get store promotion data and <this week free> games
    for e in data["data"]["Catalog"]["searchStore"]["elements"]:

        # Remove items that are discounted but not free.
        if not is_discount_game(e):
            continue

        # package free games
        try:
            query = e["catalogNs"]["mappings"][0]["pageSlug"]
            e["url"] = f"{URL_PRODUCT_PAGE}{query}"
        except TypeError:
            e["url"] = f"{URL_PRODUCT_BUNDLES}{e['productSlug']}"
        except IndexError:
            e["url"] = f"{URL_PRODUCT_PAGE}{e['productSlug']}"

        promotions.append(PromotionGame(**e))

    return promotions
