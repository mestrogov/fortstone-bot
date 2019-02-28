# -*- coding: utf-8 -*-


def translate_service_name(service):
    translated_services = {
        "Website and Forums": "Веб-сайт и форумы",
        "Game Services": "Игровые сервисы",
        "Fortnite": "Fortnite",
        "Login": "Сервисы аутентификации",
        "Parties, Friends, and Messaging": "Группы, друзья, сообщения",
        "Epic Games store": "Магазин Epic Games",
        "Voice Chat": "Голосовой чат",
        "Matchmaking": "Поиск матчей",
        "Stats and Leaderboards": "Статистика и список лидеров",
        "Store": "Внутриигровой магазин"
    }

    try:
        return translated_services[service]
    except:
        return service


def translate_service_status(status):
    translated_statuses = {
        "operational": "работает в штатном режиме",
        "under_maintenance": "на технических работах",
        "degraded_performance": "ухудшенная производительность",
        "partial_outage": "частичная недоступность"
    }

    try:
        return translated_statuses[status]
    except:
        return status
