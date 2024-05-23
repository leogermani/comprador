import mysql.connector
from config import Config

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_DATABASE
        )

    def execute_query(self, query):
        # Execute SQL queries here
        pass