import logging
import pandas as pd


class DatabaseHandler:
    """Class to handle database operations such as storing detection data."""

    def __init__(self, db_conn):
        """Initializes the DatabaseHandler with an active database connection."""
        self.db_conn = db_conn  # Use an existing DatabaseConnection object

    def store_detections(self, detections):
        """Stores detection data into the PostgreSQL database using the provided connection."""
        try:
            # Get a cursor from the existing DatabaseConnection
            cursor = self.db_conn.get_cursor()

            # Convert detections list to pandas DataFrame
            df = pd.DataFrame(detections)

            # Use COPY FROM to insert data efficiently if needed, or just simple inserts
            for _, row in df.iterrows():
                cursor.execute(
                    """
                    INSERT INTO object_detections (image_name, class_name, confidence, x_min, y_min, x_max, y_max, detection_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        row["image_name"],
                        row["class_name"],
                        row["confidence"],
                        row["x_min"],
                        row["y_min"],
                        row["x_max"],
                        row["y_max"],
                        row["detection_time"],
                    ),
                )

            # Commit the transaction
            self.db_conn.commit()
            logging.info(f"Stored {len(df)} detection records to the database.")

        except Exception as e:
            logging.error(f"Error storing detection data to the database: {e}")
            self.db_conn.rollback()  # Rollback if something goes wrong
