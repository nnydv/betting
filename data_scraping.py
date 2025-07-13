"""
Football Data Scraping Module

This module handles downloading Premier League match data from football-data.co.uk
with proper error handling, retry logic, and comprehensive logging.
"""

import logging
import time
from typing import Optional
import requests
import pandas as pd
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_scraping.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FootballDataScraper:
    """
    A class to handle scraping football match data from reliable sources.
    """
    
    def __init__(self, base_url: str = "https://www.football-data.co.uk/mmz4281"):
        """
        Initialize the scraper with base URL.
        
        Args:
            base_url: Base URL for football data source
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Football-Prediction-System/1.0'
        })
    
    def download_season_data(
        self, 
        season: str = "2324", 
        league: str = "E0",
        output_file: str = "matches.csv",
        max_retries: int = 3
    ) -> bool:
        """
        Download football match data for a specific season.
        
        Args:
            season: Season identifier (e.g., "2324" for 2023-24)
            league: League identifier (E0 for Premier League)
            output_file: Output CSV filename
            max_retries: Maximum number of retry attempts
            
        Returns:
            bool: True if download successful, False otherwise
        """
        url = f"{self.base_url}/{season}/{league}.csv"
        output_path = Path(output_file)
        
        logger.info(f"Starting download from: {url}")
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Validate content
                if len(response.content) == 0:
                    raise ValueError("Downloaded file is empty")
                
                # Save to file
                output_path.write_bytes(response.content)
                
                # Verify file was created and has content
                if output_path.exists() and output_path.stat().st_size > 0:
                    logger.info(f"✅ Successfully downloaded {output_path.stat().st_size} bytes to {output_file}")
                    return True
                else:
                    raise FileNotFoundError("File was not created or is empty")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Failed to download data after {max_retries} attempts")
                    return False
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                return False
        
        return False
    
    def validate_data(self, file_path: str) -> bool:
        """
        Validate the downloaded CSV data.
        
        Args:
            file_path: Path to the CSV file to validate
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        try:
            df = pd.read_csv(file_path)
            
            # Check if file has data
            if len(df) == 0:
                logger.error("❌ CSV file is empty")
                return False
            
            # Check for required columns
            required_columns = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.error(f"❌ Missing required columns: {missing_columns}")
                return False
            
            logger.info(f"✅ Data validation passed: {len(df)} matches found")
            return True
            
        except Exception as e:
            logger.error(f"❌ Data validation failed: {e}")
            return False


def main():
    """Main function to run the data scraping process."""
    scraper = FootballDataScraper()
    
    # Download current season data
    success = scraper.download_season_data()
    
    if success:
        # Validate the downloaded data
        if scraper.validate_data("matches.csv"):
            logger.info("🎉 Data scraping completed successfully!")
        else:
            logger.error("❌ Data validation failed")
    else:
        logger.error("❌ Data scraping failed")


if __name__ == "__main__":
    main()