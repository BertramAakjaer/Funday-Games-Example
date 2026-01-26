import logging
from dataclasses import dataclass, field
from datetime import datetime

import funday_bundle.utils as util
from funday_bundle.db_manager import DatabaseManager

@dataclass(slots=True, frozen=True)
class GameCache:
    hash: str
    steam_id: int
    title: str
    price: float # in euro
    overall_rating: float
    overall_count: int
    tags: list[str] # lower and stripped
    release_date: datetime | None
    last_time_scraped: datetime | None

@dataclass(slots=True, frozen=True)
class BundleCache:
    hash: str
    steam_id: str
    title: str
    discount: float
    total_price: float
    tags: list[str]
    games_in_bundle: list[str] # Hashes of them
    

@dataclass(slots=True)
class CachedCollection:
    # We use a special field for the DB manager so it doesn't interfere with standard dataclass behavior
    db_manager: DatabaseManager = field(init=False, repr=False)

    def __post_init__(self):
        self.db_manager = DatabaseManager()
        

    def add_game(self, game_obj: GameCache) -> bool:
        return self.db_manager.add_game(game_obj)
            
    def add_bundle(self, bundle_obj: BundleCache) -> bool:
        return self.db_manager.add_bundle(bundle_obj)
    
    def does_game_exists(self, steam_id_hash: str) -> GameCache | None:
        return self.db_manager.get_game(steam_id_hash)
    
    # Replaces the old export_to_csv logic
    def close_connections(self) -> None:
        self.db_manager.close_connection()