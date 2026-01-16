import time
from dataclasses import dataclass, field


def current_time_sec() -> int:
    return int(time.time())


@dataclass(slots=True, frozen=True)
class GameCache:
    hash: str
    steam_id: str
    title: str
    price: float # in euro
    overall_rating: float
    overall_count: int
    tags: list[str] # lower and stripped
    genres: list[str] # lower and stripped
    release_date: int
    
    # Automatically handeled
    scraped_at: int = field(default_factory=current_time_sec)

@dataclass(slots=True, frozen=True)
class BundleCache:
    hash: str
    steam_id: str
    title: str
    discount: float
    total_price: float
    tags: list[str]
    
    games_in_bundle: list[str] # Hashes of them
    
    # Automatically handeled
    scraped_at: int = field(default_factory=current_time_sec)


@dataclass(slots=True, frozen=True)
class CachedCollection:
    games: dict[str, GameCache] = field(default_factory=dict, init=False)
    bundels: dict[str, BundleCache] = field(default_factory=dict, init=False)

    def add_game(self) -> None:
        pass
    
    def add_bundle(self) -> None:
        pass
    
    def import_from_csv(self) -> None:
        pass
    
    def export_to_csv(self) -> None:
        pass