class Config:
    DATABASE_URL = get_config_value("DATABASE_URL", [str, ""])
    API_HASH = get_config_value("API_HASH", [str, "abcdedf......"])
    API_ID = get_config_value("API_ID", [int, 1234567])
    BOT_TOKEN = get_config_value("BOT_TOKEN", [str, "bot:token here"])
    COMPLETED_STR = get_config_value("COMPLETED_STR", [str, "▰"])
    REMAINING_STR = get_config_value("REMAINING_STR", [str, "▱"])
    MAX_QUEUE_SIZE = get_config_value("MAX_QUEUE_SIZE", [int, 5])
    SLEEP_SECS = get_config_value("SLEEP_SECS", [int, 10])
    IS_MONGO = get_config_value("IS_MONGO", [bool, False])
    DEFAULT_LOCALE = get_config_value("DEFAULT_LOCALE", [str, "en"])
    SESSION_STRING = get_config_value("SESSION_STRING", [str, ""])

    # Access Restriction
    IS_PRIVATE = get_config_value("IS_PRIVATE", [bool, False])
    AUTH_USERS = get_config_value("AUTH_USERS", [list, [123456789]])
    OWNER_ID = get_config_value("OWNER_ID", [int, 0])

    # Public username url or invite link of private chat
    FORCEJOIN = get_config_value("FORCEJOIN", [str, ""])
    FORCEJOIN_ID = get_config_value("FORCEJOIN_ID", [int, -100123465978])

    TRACE_CHANNEL = get_config_value("TRACE_CHANNEL", [int, 0])
    SAVE_FILE_TO_TRACE_CHANNEL = get_config_value("SAVE_FILE_TO_TRACE_CHANNEL", [bool, False])