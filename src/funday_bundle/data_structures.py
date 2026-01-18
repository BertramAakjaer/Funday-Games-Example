from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True, frozen=True)
class GameCache:
    hash: str
    steam_id: int
    title: str
    price: float # in euro
    overall_rating: float
    overall_count: int
    tags: list[str] # lower and stripped
    release_date: datetime
    last_time_scraped: datetime


@dataclass(slots=True, frozen=True)
class BundleCache:
    hash: str
    steam_id: str
    title: str
    discount: float
    total_price: float
    tags: list[str]
    
    games_in_bundle: list[str] # Hashes of them


@dataclass(slots=True, frozen=True)
class CachedCollection:
    games: dict[str, GameCache] = field(default_factory=dict, init=False)
    bundels: dict[str, BundleCache] = field(default_factory=dict, init=False)

    def add_game(self, game_obj: GameCache) -> bool:
        try:
            hash = game_obj.hash
            self.games[hash] = game_obj
            return True
        except:
            return False
            
    def add_bundle(self, bundle_obj) -> bool:
        try:
            hash = bundle_obj.hash
            self.bundels[hash] = bundle_obj
            return True
        except:
            return False
        
    # Returns Game OBJ if it exists, else None
    def does_game_exists(self, steam_id_hash: str) -> GameCache | None:
        if steam_id_hash in self.games:
            return self.games[steam_id_hash]
        else:
            return None
    
    
    def import_from_csv(self) -> None:
        pass
    
    def export_to_csv(self) -> None:
        pass