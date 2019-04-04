# -*- coding: utf-8 -*-


def translate_global_status(status):
    translated_global_statuses = {
        "All Systems Operational": "✅ Сервисы Epic Games работают в штатном режиме.",
        "Service Under Maintenance": "🚧 Некоторые из сервисов Epic Games находятся на технических работах.",
        "Partially Degraded Service": "〽️ Некоторые из сервисов Epic Games работают с ухудшенной производительностью.",
        "Minor Service Outage": "⚠️ Некоторые из сервисов Epic Games частично недоступны.",
        "Partial System Outage": "️❌ Большинство из сервисов Epic Games частично недоступны.",
        "Major Service Outage": "🚨 Сервисы Epic Games недоступны.",
    }

    try:
        return translated_global_statuses[status]
    except:
        return f"⁉️ Сервисы Epic Games не работают в штантном режиме, статус: {status}."


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
        "Store": "Внутриигровой магазин предметов"
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
