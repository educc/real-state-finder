from dataclasses import dataclass


@dataclass
class AppConfig:
    exchange_rate_pen_usd: float = 3.8
    nexo_use_cache: bool = False
    test: bool = False
    thread_size: int = 2


config = AppConfig()


def set_config(new_conf: AppConfig):
    global config
    config = new_conf


def get_config():
    return config


def is_test() -> bool:
    return config.test


def thread_size() -> int:
    return config.thread_size
