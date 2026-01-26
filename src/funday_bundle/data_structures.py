import logging
from dataclasses import dataclass, field
from datetime import datetime

import funday_bundle.utils as util
from funday_bundle.db_manager import DatabaseManager

@dataclass(slots=True, frozen=True)
class GameCache:
    hash: str # Hash of the access link, not the steam_id
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
    hash: str # Hash of the access link, not the steam_id
    steam_id: str
    title: str
    discount: float
    total_price: float
    tags: list[str]
    games_in_bundle: list[str] # Hashes of them
    

@dataclass(slots=True)
class CachedCollection:
    db_manager: DatabaseManager = field(init=False, repr=False)

    # Cached hashes from database to save time on lookup
    known_game_hashes: set[str] = field(default_factory=set, init=False)
    known_bundle_hashes: set[str] = field(default_factory=set, init=False)

    def __post_init__(self):
        self.db_manager = DatabaseManager()
        
        self.known_game_hashes = self.db_manager.get_all_game_hashes()
        self.known_bundle_hashes = self.db_manager.get_all_bundle_hashes()
        logging.info(f"Loaded {len(self.known_game_hashes)} games and {len(self.known_bundle_hashes)} bundles into memory.")

    def add_game(self, game_obj: GameCache) -> bool:
        if self.db_manager.add_game(game_obj):
            self.known_game_hashes.add(game_obj.hash)
            return True
        
        return False
            
    def add_bundle(self, bundle_obj: BundleCache) -> bool:
        if self.db_manager.add_bundle(bundle_obj):
            self.known_bundle_hashes.add(bundle_obj.hash)
            return True
        return False
    
    def does_game_exists(self, steam_id_hash: str, return_object=False) -> GameCache | bool:
        if steam_id_hash not in self.known_game_hashes:
            return False
        
        if return_object:
            game = self.db_manager.get_game(steam_id_hash)
            if game:
                return True
            else:
                return False
        return True
    
    def close_connections(self) -> None:
        self.db_manager.close_connection()