import mysql.connector
from mysql.connector import Error
import logging
from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASS
            )
            logger.info("✅ Connected to BotHost database!")
        except Error as e:
            logger.error(f"❌ Database connection failed: {e}")
    
    def create_tables(self):
        if not self.connection:
            return
            
        try:
            cursor = self.connection.cursor()
            
            # Players table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    uuid VARCHAR(36) PRIMARY KEY,
                    username VARCHAR(16) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    twofa_enabled BOOLEAN DEFAULT FALSE,
                    twofa_code VARCHAR(6),
                    telegram_chat_id VARCHAR(50),
                    authenticated BOOLEAN DEFAULT FALSE,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Purchases table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchases (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    player_uuid VARCHAR(36),
                    product_name VARCHAR(255),
                    price DECIMAL(10,2),
                    status VARCHAR(50) DEFAULT 'pending',
                    screenshot_path VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_uuid) REFERENCES players(uuid)
                )
            """)
            
            # Support tickets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS support_tickets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    player_uuid VARCHAR(36),
                    type ENUM('bug', 'complaint'),
                    target_player VARCHAR(16),
                    description TEXT,
                    status VARCHAR(50) DEFAULT 'open',
                    admin_response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_uuid) REFERENCES players(uuid)
                )
            """)
            
            self.connection.commit()
            cursor.close()
            logger.info("✅ Database tables created successfully!")
            
        except Error as e:
            logger.error(f"❌ Failed to create tables: {e}")
    
    # Player methods
    def user_exists(self, username):
        if not self.connection:
            return False
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM players WHERE username = %s", (username,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] > 0 if result else False
        except Error as e:
            logger.error(f"Error checking user: {e}")
            return False
    
    def verify_password(self, username, password):
        if not self.connection:
            return False
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT password_hash FROM players WHERE username = %s", (username,))
            result = cursor.fetchone()
            cursor.close()
            
            if result and result[0]:
                return result[0] == password  # В реальности нужно хеширование
            return False
        except Error as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def update_telegram_chat_id(self, username, chat_id):
        if not self.connection:
            return
            
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE players SET telegram_chat_id = %s WHERE username = %s",
                (chat_id, username)
            )
            self.connection.commit()
            cursor.close()
            logger.info(f"Telegram chat ID updated for {username}")
        except Error as e:
            logger.error(f"Failed to update chat ID: {e}")
    
    # 2FA methods
    def is_twofa_enabled(self, username):
        if not self.connection:
            return False
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT twofa_enabled FROM players WHERE username = %s", (username,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else False
        except Error as e:
            logger.error(f"2FA check failed: {e}")
            return False
    
    def save_2fa_code(self, username, code):
        if not self.connection:
            return
            
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE players SET twofa_code = %s WHERE username = %s",
                (code, username)
            )
            self.connection.commit()
            cursor.close()
            logger.info(f"2FA code saved for {username}")
        except Error as e:
            logger.error(f"Failed to save 2FA code: {e}")
    
    # Shop methods
    def create_purchase(self, username, product_name, price):
        if not self.connection:
            return
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO purchases (player_uuid, product_name, price)
                SELECT uuid, %s, %s FROM players WHERE username = %s
            """, (product_name, price, username))
            self.connection.commit()
            cursor.close()
            logger.info(f"Purchase created for {username}: {product_name}")
        except Error as e:
            logger.error(f"Failed to create purchase: {e}")
    
    # Support methods
    def create_support_ticket(self, username, ticket_type, target_player, description):
        if not self.connection:
            return
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO support_tickets (player_uuid, type, target_player, description)
                SELECT uuid, %s, %s, %s FROM players WHERE username = %s
            """, (ticket_type, target_player, description, username))
            self.connection.commit()
            cursor.close()
            logger.info(f"Support ticket created for {username}")
        except Error as e:
            logger.error(f"Failed to create support ticket: {e}")
    
    def close(self):
        if self.connection:
            self.connection.close()