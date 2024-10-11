import os
from dotenv import load_dotenv
import logging
import psycopg2


class DatabaseConnection:
    def __init__(self):
        self.db_name = None
        self.user = None
        self.password = None
        self.host = None
        self.port = None
        self.conn = None
        self.load_env_variables()

    def load_env_variables(self):
        """Load database connection details from the .env file."""
        load_dotenv()  # Load environment variables from .env file
        self.db_name = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")

    def connect(self):
        """Establishes a connection to the PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(
                dbname=self.db_name,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            logging.info("Database connection established.")
        except psycopg2.Error as e:
            logging.error(f"Error connecting to PostgreSQL: {e}")
            raise

    def disconnect(self):
        """Closes the connection to the database."""
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")

    def get_cursor(self):
        """Returns a cursor for executing database queries."""
        if not self.conn:
            self.connect()
        return self.conn.cursor()

    def commit(self):
        """Commits the current transaction."""
        if self.conn:
            self.conn.commit()
