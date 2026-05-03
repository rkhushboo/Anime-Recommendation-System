"""
Utility Functions for Anime Recommendation System
Data processing, cleaning, and visualization helpers
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import streamlit as st
import warnings

warnings.filterwarnings('ignore')


def load_data(anime_path, rating_path):
    """
    Load and return anime and rating datasets
    
    Args:
        anime_path: Path to anime.csv
        rating_path: Path to rating.csv
        
    Returns:
        Tuple of (anime_df, rating_df)
    """
    try:
        anime_df = pd.read_csv(anime_path)
        rating_df = pd.read_csv(rating_path)
        print(f"✓ Datasets loaded successfully")
        return anime_df, rating_df
    except Exception as e:
        print(f"✗ Error loading datasets: {e}")
        raise


def clean_data(anime_df, rating_df):
    """
    Clean and preprocess datasets
    
    Args:
        anime_df: Anime DataFrame
        rating_df: Rating DataFrame
        
    Returns:
        Tuple of (cleaned_anime_df, cleaned_rating_df)
    """
    print("Cleaning datasets...")
    
    # ===== ANIME DATA CLEANING =====
    anime_df = anime_df.copy()
    
    # Handle missing values
    anime_df['rating'] = pd.to_numeric(anime_df['rating'], errors='coerce')
    anime_df['rating'] = anime_df['rating'].replace(-1, np.nan)
    anime_df['rating'] = anime_df['rating'].fillna(anime_df['rating'].median())
    
    anime_df['members'] = pd.to_numeric(anime_df['members'], errors='coerce')
    anime_df['members'] = anime_df['members'].fillna(0)
    
    # Clean genre column
    anime_df['genre'] = anime_df['genre'].fillna('Unknown')
    anime_df['genre'] = anime_df['genre'].str.strip()
    
    # Remove duplicates
    anime_df = anime_df.drop_duplicates(subset=['anime_id'], keep='first')
    
    # ===== RATING DATA CLEANING =====
    rating_df = rating_df.copy()
    
    # Replace -1 ratings with NaN
    rating_df['rating'] = pd.to_numeric(rating_df['rating'], errors='coerce')
    rating_df = rating_df[rating_df['rating'] != -1]
    rating_df = rating_df.dropna(subset=['rating'])
    
    # Remove duplicates
    rating_df = rating_df.drop_duplicates(
        subset=['user_id', 'anime_id'],
        keep='first'
    )
    
    # Keep only anime that exist in anime_df
    valid_anime_ids = anime_df['anime_id'].unique()
    rating_df = rating_df[rating_df['anime_id'].isin(valid_anime_ids)]
    
    print(f"✓ Data cleaned successfully")
    print(f"  - Anime records: {len(anime_df)}")
    print(f"  - Rating records: {len(rating_df)}")
    
    return anime_df.reset_index(drop=True), rating_df.reset_index(drop=True)


def get_dataset_stats(anime_df, rating_df):
    """
    Get comprehensive dataset statistics
    
    Args:
        anime_df: Anime DataFrame
        rating_df: Rating DataFrame
        
    Returns:
        Dictionary of statistics
    """
    stats = {
        'total_anime': len(anime_df),
        'total_users': rating_df['user_id'].nunique(),
        'total_ratings': len(rating_df),
        'avg_anime_rating': anime_df['rating'].mean(),
        'avg_user_ratings': len(rating_df) / rating_df['user_id'].nunique(),
        'rating_range': (anime_df['rating'].min(), anime_df['rating'].max()),
        'genres': anime_df['genre'].nunique(),
    }
    return stats


def plot_top_anime_by_rating(anime_df, top_n=10):
    """Plot top anime by rating"""
    top_anime = anime_df.nlargest(top_n, 'rating')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(top_anime['name'], top_anime['rating'], color='skyblue', edgecolor='navy')
    
    # Add value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, 
                f'{width:.1f}', ha='left', va='center', fontsize=9)
    
    ax.set_xlabel('Rating', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 Anime by Rating', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 10)
    
    plt.tight_layout()
    return fig


def plot_most_popular_anime(anime_df, top_n=10):
    """Plot most popular anime by members"""
    top_popular = anime_df.nlargest(top_n, 'members')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(top_popular['name'], top_popular['members']/1e6, 
                   color='lightcoral', edgecolor='darkred')
    
    # Add value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, 
                f'{width:.1f}M', ha='left', va='center', fontsize=9)
    
    ax.set_xlabel('Members (Millions)', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 Most Popular Anime', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig


def plot_rating_distribution(anime_df):
    """Plot distribution of anime ratings"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(anime_df['rating'].dropna(), bins=30, color='mediumseagreen', 
            edgecolor='darkgreen', alpha=0.7)
    
    ax.axvline(anime_df['rating'].mean(), color='red', linestyle='--', 
               linewidth=2, label=f"Mean: {anime_df['rating'].mean():.2f}")
    ax.axvline(anime_df['rating'].median(), color='orange', linestyle='--', 
               linewidth=2, label=f"Median: {anime_df['rating'].median():.2f}")
    
    ax.set_xlabel('Rating', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax.set_title('Distribution of Anime Ratings', fontsize=14, fontweight='bold')
    ax.legend()
    
    plt.tight_layout()
    return fig


def plot_wordcloud_genres(anime_df):
    """Generate and plot wordcloud of genres"""
    # Combine all genres
    all_genres = ' '.join(anime_df['genre'].fillna('').values)
    
    # Remove common stop words and create wordcloud
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='viridis',
        max_words=100
    ).generate(all_genres)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title('Anime Genres WordCloud', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    return fig


def plot_rating_vs_members(anime_df):
    """Plot scatter of rating vs members"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scatter = ax.scatter(anime_df['members']/1e6, anime_df['rating'], 
                        alpha=0.6, s=50, c=anime_df['rating'], 
                        cmap='coolwarm', edgecolors='black', linewidth=0.5)
    
    ax.set_xlabel('Members (Millions)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Rating', fontsize=12, fontweight='bold')
    ax.set_title('Anime Rating vs Popularity (Members)', fontsize=14, fontweight='bold')
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Rating', fontweight='bold')
    
    plt.tight_layout()
    return fig


def format_large_number(num):
    """Format large numbers for display"""
    if num >= 1e6:
        return f"{num/1e6:.1f}M"
    elif num >= 1e3:
        return f"{num/1e3:.1f}K"
    else:
        return f"{int(num)}"


def display_recommendations_table(recommendations_df):
    """Display recommendations as a formatted table"""
    if 'error' in recommendations_df.columns:
        st.warning(f"⚠️ {recommendations_df['error'].iloc[0]}")
        return False
    
    if len(recommendations_df) == 0:
        st.warning("⚠️ No recommendations found")
        return False
    
    # Format the dataframe for display
    display_df = recommendations_df.copy()
    display_df['Rating'] = display_df['rating'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
    display_df['Score'] = display_df['score'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(
        display_df[['name', 'genre', 'Rating', 'Score']].rename(columns={
            'name': 'Anime Name',
            'genre': 'Genre'
        }),
        use_container_width=True,
        hide_index=True
    )
    
    return True


def display_anime_stats(stats):
    """Display dataset statistics in a nice format"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total Anime", stats['total_anime'])
    
    with col2:
        st.metric("👥 Total Users", stats['total_users'])
    
    with col3:
        st.metric("⭐ Total Ratings", stats['total_ratings'])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 Avg Anime Rating", f"{stats['avg_anime_rating']:.2f}")
    
    with col2:
        st.metric("📋 Avg Ratings/User", f"{stats['avg_user_ratings']:.1f}")
    
    with col3:
        st.metric("🎨 Unique Genres", stats['genres'])


def get_genre_options(anime_df):
    """Extract unique genres for filtering"""
    genres = set()
    for genre_string in anime_df['genre'].dropna():
        if isinstance(genre_string, str):
            individual_genres = [g.strip() for g in genre_string.split(',')]
            genres.update(individual_genres)
    
    return sorted(list(genres))


def validate_user_id(user_id, rating_df):
    """Check if user ID exists in rating data"""
    return user_id in rating_df['user_id'].values


def validate_anime_name(anime_name, anime_df):
    """Check if anime name exists"""
    return anime_name.lower() in anime_df['name'].str.lower().values


@st.cache_data
def cache_recommendation_results(mode, param1, param2, param3):
    """Cache recommendation results (optional optimization)"""
    return None
