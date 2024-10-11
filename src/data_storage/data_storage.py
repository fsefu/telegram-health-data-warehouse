import logging
import ast  # Import ast to safely evaluate string representations of lists
import numpy as np


class DataStorage:
    def __init__(self, db_conn):
        """Initialize the DataStorage with a DatabaseConnection object."""
        self.db_conn = db_conn

    def create_table(self):
        """Creates a table to store the cleaned data."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS cleaned_data (
            post_id VARCHAR PRIMARY KEY, 
            channel_name VARCHAR ,
            channel_username VARCHAR ,
            message_text TEXT NOT NULL,
            views BIGINT,  -- Changed views to BIGINT
            timestamp TIMESTAMP,
            image_urls TEXT[],
            image_paths TEXT[],
            source VARCHAR 
            
        );
        """
        try:
            cursor = self.db_conn.get_cursor()
            cursor.execute(create_table_query)
            self.db_conn.commit()
            logging.info("Table 'cleaned_data' created successfully.")
        except Exception as e:
            logging.error(f"Error creating table: {e}")
            self.db_conn.conn.rollback()
        finally:
            cursor.close()

    def convert_list_to_pg_array(self, lst):
        """Convert a Python list to PostgreSQL array format."""
        if isinstance(lst, list):
            return "{" + ",".join(f'"{item}"' for item in lst) + "}"
        return lst  # Return as-is if it's not a list

    def store_cleaned_data(self, cleaned_data):
        """Store cleaned data into PostgreSQL."""
        try:
            cursor = self.db_conn.get_cursor()
            # Iterate through each row in the cleaned data
            for index, row in cleaned_data.iterrows():

                views_value = int(row["views"]) if not np.isnan(row["views"]) else 0

                # Optionally, add a check for extreme values
                if (
                    views_value < -9223372036854775808
                    or views_value > 9223372036854775807
                ):
                    logging.warning(
                        f"views_value {views_value} is out of range for BIGINT, setting to 0."
                    )
                    views_value = 0

                # Convert string representations of lists to actual lists
                image_urls_list = (
                    ast.literal_eval(row["image_urls"])
                    if isinstance(row["image_urls"], str)
                    else row["image_urls"]
                )
                image_paths_list = (
                    ast.literal_eval(row["image_paths"])
                    if isinstance(row["image_paths"], str)
                    else row["image_paths"]
                )

                # Convert specific columns to PostgreSQL array format
                image_urls_pg = self.convert_list_to_pg_array(image_urls_list)
                image_paths_pg = self.convert_list_to_pg_array(image_paths_list)

                # Construct the SQL query to insert data
                insert_query = """
                INSERT INTO cleaned_data (post_id, channel_name, channel_username, message_text, views, timestamp, image_urls, image_paths, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                # Log the values being inserted for debugging
                logging.info(
                    f"Inserting data: post_id={row['post_id']}, message_text={row['message_text']}, views={row['views']}, "
                    f"timestamp={row['timestamp']}, image_urls={image_urls_pg}, image_paths={image_paths_pg}"
                )

                # Execute the insert command
                cursor.execute(
                    insert_query,
                    (
                        row["post_id"],
                        row["channel_name"],
                        row["channel_username"],
                        row["message_text"],
                        views_value,
                        row["timestamp"],
                        image_urls_pg,
                        image_paths_pg,
                        row["source"],
                    ),
                )

            self.db_conn.commit()
            logging.info("Cleaned data inserted successfully.")
        except Exception as e:
            logging.error(f"Error inserting cleaned data: {e}")
            self.db_conn.rollback()
        finally:
            cursor.close()
