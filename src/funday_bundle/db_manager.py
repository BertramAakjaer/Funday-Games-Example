import sqlite3
import json
import logging
from datetime import datetime
from funday_bundle.data_structures import GameCache, BundleCache

class DatabaseManager:
    def __init__(self, db_path: str = "scraped_data/steam_games_n_bundles.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        
        # Games Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                hash TEXT PRIMARY KEY,
                steam_id INTEGER,
                title TEXT,
                price REAL,
                overall_rating REAL,
                overall_count INTEGER,
                tags TEXT,
                release_date TEXT,
                last_time_scraped TEXT
            )
        ''')

        # Bundles Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bundles (
                hash TEXT PRIMARY KEY,
                steam_id TEXT,
                title TEXT,
                discount REAL,
                total_price REAL,
                tags TEXT,
                games_in_bundle TEXT
            )
        ''')
        
        # Inside _create_tables(self)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bundle_contents (
                game_hash TEXT,
                bundle_hash TEXT,
                PRIMARY KEY (game_hash, bundle_hash)
            )
        ''')
        # Note: The Primary Key (game_hash, bundle_hash) automatically indexes 
        # game_hash, making lookups extremely fast.
        
        self.conn.commit()

    def add_game(self, game: 'GameCache') -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO games 
                (hash, steam_id, title, price, overall_rating, overall_count, tags, release_date, last_time_scraped)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                game.hash,
                game.steam_id,
                game.title,
                game.price,
                game.overall_rating,
                game.overall_count,
                json.dumps(game.tags), # Convert list to JSON string
                game.release_date.isoformat() if game.release_date else None,
                game.last_time_scraped.isoformat() if game.last_time_scraped else None
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Failed to add game to DB: {e}")
            return False

    def get_game(self, game_hash: str) -> GameCache | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM games WHERE hash = ?", (game_hash,))
        row = cursor.fetchone()

        if row:
            try:
                return GameCache(
                    hash=row['hash'],
                    steam_id=row['steam_id'],
                    title=row['title'],
                    price=row['price'],
                    overall_rating=row['overall_rating'],
                    overall_count=row['overall_count'],
                    tags=json.loads(row['tags']) if row['tags'] else [],
                    release_date=datetime.fromisoformat(row['release_date']),
                    last_time_scraped=datetime.fromisoformat(row['last_time_scraped'])
                )
            except Exception as e:
                logging.error(f"Error parsing game from DB: {e}")
                return None
        return None
    

    def add_bundle(self, bundle: 'BundleCache') -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO bundles 
                (hash, steam_id, title, discount, total_price, tags, games_in_bundle)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                bundle.hash,
                bundle.steam_id,
                bundle.title,
                bundle.discount,
                bundle.total_price,
                json.dumps(bundle.tags),
                json.dumps(bundle.games_in_bundle)
            ))
            
            
            # Prepare list of tuples for bulk insertion: [(game1, bundleA), (game2, bundleA)]
            contents_data = [(g_hash, bundle.hash) for g_hash in bundle.games_in_bundle]

            cursor.executemany('''
                INSERT OR IGNORE INTO bundle_contents (game_hash, bundle_hash)
                VALUES (?, ?)
            ''', contents_data)


            self.conn.commit()
            return True
        
        except Exception as e:
            logging.error(f"Failed to add bundle to DB: {e}")
            return False
    
    def get_bundle(self, bundle_hash: str) -> BundleCache | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM bundles WHERE hash = ?", (bundle_hash,))
        row = cursor.fetchone()

        if row:
            try:
                return BundleCache(
                    hash=row['hash'],
                    steam_id=row['steam_id'],
                    title=row['title'],
                    discount=row['discount'],
                    total_price=row['total_price'],
                    tags=json.loads(row['tags']) if row['tags'] else [],
                    games_in_bundle=json.loads(row['games_in_bundle']) if row['games_in_bundle'] else []
                )
            except Exception as e:
                logging.error(f"Error parsing game from DB: {e}")
                return None
        return None
    
    
    def get_all_game_hashes(self) -> set[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT hash FROM games")
        return {row['hash'] for row in cursor.fetchall()}

    def get_all_bundle_hashes(self) -> set[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT hash FROM bundles")
        return {row['hash'] for row in cursor.fetchall()}
    
    
    def get_bundles_containing_game(self, game_hash: str) -> list[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT bundle_hash FROM bundle_contents WHERE game_hash = ?", (game_hash,))
        return [row['bundle_hash'] for row in cursor.fetchall()]
    
    
    

    def close_connection(self):
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")