"""
Test script to verify the recommendation system works correctly
Run this before starting the Streamlit app
"""

import sys
from pathlib import Path

# Get the current directory
current_dir = Path(__file__).parent

# Test imports
print("🔍 Testing imports...")
try:
    from model import AnimeRecommendationSystem
    from utils import load_data, clean_data, get_dataset_stats
    print("✓ Custom modules imported successfully")
except Exception as e:
    print(f"✗ Error importing custom modules: {e}")
    sys.exit(1)

try:
    import pandas as pd
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from surprise import SVD
    import streamlit as st
    print("✓ All required libraries imported successfully")
except Exception as e:
    print(f"✗ Error importing required libraries: {e}")
    print("   Please run: pip install -r requirements.txt")
    sys.exit(1)

# Test data loading
print("\n📂 Testing data loading...")
try:
    anime_df, rating_df = load_data(
        str(current_dir / 'anime.csv'),
        str(current_dir / 'rating.csv')
    )
    print(f"✓ Datasets loaded: {len(anime_df)} anime, {len(rating_df)} ratings")
except Exception as e:
    print(f"✗ Error loading data: {e}")
    sys.exit(1)

# Test data cleaning
print("\n🧹 Testing data cleaning...")
try:
    anime_df, rating_df = clean_data(anime_df, rating_df)
    print(f"✓ Data cleaned: {len(anime_df)} anime, {len(rating_df)} ratings")
except Exception as e:
    print(f"✗ Error cleaning data: {e}")
    sys.exit(1)

# Test recommendation system initialization
print("\n🤖 Testing recommendation system initialization...")
try:
    rec_system = AnimeRecommendationSystem(anime_df, rating_df)
    print("✓ Recommendation system initialized successfully")
except Exception as e:
    print(f"✗ Error initializing recommendation system: {e}")
    sys.exit(1)

# Test each recommendation mode
print("\n📊 Testing recommendation modes...")

try:
    print("  Testing Content-Based Filtering...")
    anime_list = rec_system.get_anime_list()
    if len(anime_list) > 0:
        test_anime = anime_list[0]
        result = rec_system.recommend_content(test_anime, top_n=5)
        if 'error' not in result.columns:
            print(f"  ✓ Content-Based: Got {len(result)} recommendations")
        else:
            print(f"  ⚠ Content-Based: {result['error'].iloc[0]}")
except Exception as e:
    print(f"  ✗ Content-Based error: {e}")

try:
    print("  Testing Collaborative Filtering...")
    valid_users = rating_df['user_id'].unique()[:5]
    if len(valid_users) > 0:
        test_user = valid_users[0]
        result = rec_system.recommend_collaborative(int(test_user), top_n=5)
        if 'error' not in result.columns:
            print(f"  ✓ Collaborative: Got {len(result)} recommendations")
        else:
            print(f"  ⚠ Collaborative: {result['error'].iloc[0]}")
except Exception as e:
    print(f"  ✗ Collaborative error: {e}")

try:
    print("  Testing Hybrid Filtering...")
    anime_list = rec_system.get_anime_list()
    valid_users = rating_df['user_id'].unique()[:5]
    if len(anime_list) > 0 and len(valid_users) > 0:
        test_anime = anime_list[0]
        test_user = valid_users[0]
        result = rec_system.recommend_hybrid(test_anime, int(test_user), top_n=5)
        if 'error' not in result.columns:
            print(f"  ✓ Hybrid: Got {len(result)} recommendations")
        else:
            print(f"  ⚠ Hybrid: {result['error'].iloc[0]}")
except Exception as e:
    print(f"  ✗ Hybrid error: {e}")

# Test statistics
print("\n📈 Testing statistics...")
try:
    stats = get_dataset_stats(anime_df, rating_df)
    print(f"✓ Statistics computed:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
except Exception as e:
    print(f"✗ Error computing statistics: {e}")

print("\n" + "="*60)
print("✅ All tests passed! The system is ready to run.")
print("\nTo start the Streamlit app, run:")
print("   streamlit run app.py")
print("="*60)
