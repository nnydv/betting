"""
Football Data Cleaning Module

This module handles cleaning and preprocessing of raw football match data
with comprehensive error handling, data validation, and logging.
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_cleaning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FootballDataCleaner:
    """
    A class to handle cleaning and preprocessing of football match data.
    """
    
    def __init__(self):
        """Initialize the data cleaner."""
        self.required_columns = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]
        self.output_columns = ["date", "home_team", "away_team", "home_goals", "away_goals", "result"]
    
    def load_raw_data(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Load raw match data from CSV file.
        
        Args:
            file_path: Path to the raw data CSV file
            
        Returns:
            DataFrame with raw data or None if loading fails
        """
        try:
            if not Path(file_path).exists():
                logger.error(f"❌ File not found: {file_path}")
                return None
            
            df = pd.read_csv(file_path)
            logger.info(f"✅ Loaded {len(df)} records from {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to load data from {file_path}: {e}")
            return None
    
    def validate_raw_data(self, df: pd.DataFrame) -> bool:
        """
        Validate that raw data contains required columns and data.
        
        Args:
            df: Raw data DataFrame
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        try:
            # Check if DataFrame is empty
            if len(df) == 0:
                logger.error("❌ DataFrame is empty")
                return False
            
            # Check for required columns
            missing_columns = [col for col in self.required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"❌ Missing required columns: {missing_columns}")
                return False
            
            # Check for data types and valid values
            if not pd.api.types.is_numeric_dtype(df['FTHG']):
                logger.warning("⚠️ FTHG column is not numeric, attempting conversion")
            
            if not pd.api.types.is_numeric_dtype(df['FTAG']):
                logger.warning("⚠️ FTAG column is not numeric, attempting conversion")
            
            # Check for valid result values
            valid_results = {'H', 'D', 'A'}
            invalid_results = set(df['FTR'].unique()) - valid_results
            if invalid_results:
                logger.warning(f"⚠️ Found invalid result values: {invalid_results}")
            
            logger.info("✅ Raw data validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Data validation failed: {e}")
            return False
    
    def clean_data(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Clean and preprocess the football match data.
        
        Args:
            df: Raw data DataFrame
            
        Returns:
            Cleaned DataFrame or None if cleaning fails
        """
        try:
            logger.info("🧹 Starting data cleaning process...")
            
            # Select and rename columns
            df_clean = df[self.required_columns].copy()
            df_clean.columns = self.output_columns
            
            # Convert data types
            df_clean['home_goals'] = pd.to_numeric(df_clean['home_goals'], errors='coerce')
            df_clean['away_goals'] = pd.to_numeric(df_clean['away_goals'], errors='coerce')
            
            # Convert date column
            df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce')
            
            # Remove rows with missing critical data
            initial_count = len(df_clean)
            df_clean = df_clean.dropna(subset=['home_goals', 'away_goals', 'result', 'date'])
            
            if len(df_clean) < initial_count:
                logger.warning(f"⚠️ Removed {initial_count - len(df_clean)} rows with missing data")
            
            # Validate goal scores (should be non-negative)
            invalid_goals = (df_clean['home_goals'] < 0) | (df_clean['away_goals'] < 0)
            if invalid_goals.any():
                logger.warning(f"⚠️ Found {invalid_goals.sum()} rows with negative goal scores, removing...")
                df_clean = df_clean[~invalid_goals]
            
            # Validate result values
            df_clean = df_clean[df_clean['result'].isin(['H', 'D', 'A'])]
            
            # Sort by date
            df_clean = df_clean.sort_values('date').reset_index(drop=True)
            
            logger.info(f"✅ Data cleaning completed: {len(df_clean)} clean records")
            return df_clean
            
        except Exception as e:
            logger.error(f"❌ Data cleaning failed: {e}")
            return None
    
    def add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add derived features to the cleaned data.
        
        Args:
            df: Cleaned data DataFrame
            
        Returns:
            DataFrame with additional features
        """
        try:
            logger.info("🔧 Adding derived features...")
            
            df_enhanced = df.copy()
            
            # Total goals
            df_enhanced['total_goals'] = df_enhanced['home_goals'] + df_enhanced['away_goals']
            
            # Goal difference
            df_enhanced['goal_difference'] = df_enhanced['home_goals'] - df_enhanced['away_goals']
            
            # Match outcome as numeric
            df_enhanced['home_win'] = (df_enhanced['result'] == 'H').astype(int)
            df_enhanced['draw'] = (df_enhanced['result'] == 'D').astype(int)
            df_enhanced['away_win'] = (df_enhanced['result'] == 'A').astype(int)
            
            # High scoring match indicator
            df_enhanced['high_scoring'] = (df_enhanced['total_goals'] >= 3).astype(int)
            
            # Extract month and day of week
            df_enhanced['month'] = df_enhanced['date'].dt.month
            df_enhanced['day_of_week'] = df_enhanced['date'].dt.dayofweek
            
            logger.info(f"✅ Added {len(df_enhanced.columns) - len(df.columns)} derived features")
            return df_enhanced
            
        except Exception as e:
            logger.error(f"❌ Failed to add derived features: {e}")
            return df
    
    def save_cleaned_data(self, df: pd.DataFrame, output_file: str = "cleaned_matches.csv") -> bool:
        """
        Save cleaned data to CSV file.
        
        Args:
            df: Cleaned data DataFrame
            output_file: Output filename
            
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            df.to_csv(output_file, index=False)
            logger.info(f"✅ Cleaned data saved to {output_file}")
            
            # Provide summary statistics
            logger.info(f"📊 Data Summary:")
            logger.info(f"   - Total matches: {len(df)}")
            logger.info(f"   - Date range: {df['date'].min()} to {df['date'].max()}")
            logger.info(f"   - Home wins: {(df['result'] == 'H').sum()}")
            logger.info(f"   - Draws: {(df['result'] == 'D').sum()}")
            logger.info(f"   - Away wins: {(df['result'] == 'A').sum()}")
            logger.info(f"   - Average goals per match: {df['total_goals'].mean():.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save cleaned data: {e}")
            return False


def main():
    """Main function to run the data cleaning process."""
    cleaner = FootballDataCleaner()
    
    # Load raw data
    raw_data = cleaner.load_raw_data("matches.csv")
    if raw_data is None:
        logger.error("❌ Failed to load raw data")
        return
    
    # Validate raw data
    if not cleaner.validate_raw_data(raw_data):
        logger.error("❌ Raw data validation failed")
        return
    
    # Clean data
    cleaned_data = cleaner.clean_data(raw_data)
    if cleaned_data is None:
        logger.error("❌ Data cleaning failed")
        return
    
    # Add derived features
    enhanced_data = cleaner.add_derived_features(cleaned_data)
    
    # Save cleaned data
    if cleaner.save_cleaned_data(enhanced_data):
        logger.info("🎉 Data cleaning process completed successfully!")
    else:
        logger.error("❌ Failed to save cleaned data")


if __name__ == "__main__":
    main()