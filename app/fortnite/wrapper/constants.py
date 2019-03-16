# -*- coding: utf-8 -*-

OAUTH_TOKEN = "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token"
OAUTH_EXCHANGE = "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/exchange"
ACCOUNT_LOOKUP = "https://persona-public-service-prod06.ol.epicgames.com/persona/api/public/account/lookup?q={}"
PLAYER_STATS = "https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/stats/accountId/{}/bulk/window/alltime"
SERVER_STATUS = "https://lightswitch-public-service-prod06.ol.epicgames.com/lightswitch/api/service/bulk/status?serviceId=Fortnite"
ITEM_STORE = "https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/storefront/v2/catalog"
INGAME_NEWS = "https://fortnitecontent-website-prod07.ol.epicgames.com/content/api/pages/fortnite-game"
FORTNITE_PATCH_NOTES = "https://www.epicgames.com/fortnite/api/blog/getPosts"


class Platform:
    pc = "pc"
    ps4 = "ps4"
    xb1 = "xb1"


class Mode:
    solo = "_p2"
    duo = "_p10"
    squad = "_p9"
