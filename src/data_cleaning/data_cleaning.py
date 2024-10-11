import pandas as pd
import numpy as np
import logging


class DataCleaning:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    def remove_unwanted_rows(self):
        """Remove rows where 'message_text' is empty or starts with 'Channel'."""
        logging.info("Removing unwanted rows...")
        # Remove rows where 'message_text' is empty or starts with 'Channel'
        self.raw_data = self.raw_data.dropna(subset=["message_text"])
        self.raw_data = self.raw_data[
            ~self.raw_data["message_text"].str.startswith("Channel")
        ]
        return self.raw_data

    def fill_views_with_average(self):
        """Replace missing 'views' values with the average of five rows above and below."""
        logging.info("Filling missing 'views' values with average of neighbors...")
        # Ensure 'views' is numeric (handle cases like '2.0K' by converting them to actual numbers)
        # Assuming self.raw_data["views"] contains the views column
        self.raw_data["views"] = (
            self.raw_data["views"]
            .replace({"K": "e3", "M": "e6"}, regex=True)  # Convert K and M suffixes
            .apply(
                pd.to_numeric, errors="coerce"
            )  # Convert to numeric, handling errors
            .replace("", np.nan)  # Handle empty strings as NaN
            .astype(float)
        )

        # Find indices with missing 'views' values
        missing_views_indices = self.raw_data[self.raw_data["views"].isna()].index

        for idx in missing_views_indices:
            # Get the five rows before and after the current row, ignore NaNs
            window = self.raw_data["views"].iloc[max(0, idx - 5) : idx + 5].dropna()
            if not window.empty:
                # Replace missing 'views' with the mean of the window
                self.raw_data.at[idx, "views"] = window.mean()

        return self.raw_data

    def standardize_formats(self):
        """Standardize data formats like dates and views."""
        logging.info("Standardizing formats...")
        # Example: Convert timestamp to datetime format
        if "timestamp" in self.raw_data.columns:
            self.raw_data["timestamp"] = pd.to_datetime(
                self.raw_data["timestamp"], errors="coerce"
            )
        return self.raw_data

    def clean_data(self):
        """Run all data cleaning steps."""
        self.raw_data = self.remove_unwanted_rows()
        self.raw_data = self.fill_views_with_average()
        self.raw_data = self.standardize_formats()
        self.raw_data = self.raw_data.drop(columns=["author"])

        logging.info("Data cleaned successfully.")
        return self.raw_data


# Example usage
# raw_data = pd.read_csv('your_data_file.csv')
# cleaner = DataCleaning(raw_data)
# cleaned_data = cleaner.clean_data()
