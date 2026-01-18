import logging

from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd

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
        import ast  # Required to safely parse the string representation of lists

        try:
            # Load data, handling cases where file might not exist yet
            df = pd.read_csv("scraped_data/games.csv")
        except FileNotFoundError:
            return 

        for _, row in df.iterrows():
            try:
                # 1. Parse Tags (convert string "['a', 'b']" -> list ['a', 'b'])
                tags = ast.literal_eval(row['tags']) if pd.notna(row['tags']) else []

                # 2. Parse Dates (convert ISO strings -> datetime objects)
                # Handle potential NaNs if data was missing during export
                if pd.notna(row['release_date']):
                    release_date = datetime.fromisoformat(row['release_date'])
                else:
                    release_date = None

                if pd.notna(row['last_time_scraped']):
                    last_time_scraped = datetime.fromisoformat(row['last_time_scraped'])
                else:
                    last_time_scraped = None

                if not (release_date and last_time_scraped):
                    logging.error(f"Failed to parse row {row}")
                    continue

                # 3. Reconstruct GameCache object
                game = GameCache(
                    hash=str(row['hash']),
                    steam_id=int(row['steam_id']),
                    title=str(row['title']),
                    price=float(row['price']),
                    overall_rating=float(row['overall_rating']),
                    overall_count=int(row['overall_count']),
                    tags=tags,
                    release_date=release_date,
                    last_time_scraped=last_time_scraped
                )

                # 4. Add to internal dictionary
                self.games[game.hash] = game

            except Exception as e:
                logging.error(f"Failed to parse row {row}:\n{e}")
                continue
    
    def export_to_csv(self) -> None:
        data_rows = []
        
        for game in self.games.values():
            # Construct dictionary manually since vars() fails with slots=True
            row = {
                "hash": game.hash,
                "steam_id": game.steam_id,
                "title": game.title,
                "price": game.price,
                "overall_rating": game.overall_rating,
                "overall_count": game.overall_count,
                "tags": game.tags,
                # Convert datetimes to isoformat strings
                "release_date": game.release_date.isoformat() if isinstance(game.release_date, datetime) else None,
                "last_time_scraped": game.last_time_scraped.isoformat() if isinstance(game.last_time_scraped, datetime) else None
            }
            data_rows.append(row)

        df = pd.DataFrame(data_rows)
        # Ensure the output matches the requested path
        df.to_csv("scraped_data/games.csv", index=False)