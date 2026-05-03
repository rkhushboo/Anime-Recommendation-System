"""
Anime Recommendation System - Streamlit Web App
Interactive recommendation system with multiple filtering modes
Author: ML Engineering Team
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Import custom modules
from model import AnimeRecommendationSystem
from utils import (
    load_data,
    clean_data,
    get_dataset_stats,
    plot_top_anime_by_rating,
    plot_most_popular_anime,
    plot_rating_distribution,
    plot_wordcloud_genres,
    plot_rating_vs_members,
    display_recommendations_table,
    display_anime_stats,
    get_genre_options,
    validate_user_id,
    validate_anime_name,
    format_large_number
)


# ===== PAGE CONFIGURATION =====
st.set_page_config(
    page_title="Anime Recommendation System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2em;
        color: gray;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)


# ===== DATA LOADING & CACHING =====
@st.cache_resource
def load_recommendation_system():
    """Load and initialize recommendation system"""
    try:
        # Get the current directory
        current_dir = Path(__file__).parent
        
        # Load data
        anime_df, rating_df = load_data(
            str(current_dir / 'anime.csv'),
            str(current_dir / 'rating.csv')
        )
        
        # Clean data
        anime_df, rating_df = clean_data(anime_df, rating_df)
        
        # Initialize recommendation system
        rec_system = AnimeRecommendationSystem(anime_df, rating_df)
        
        return rec_system, anime_df, rating_df
    
    except Exception as e:
        st.error(f"❌ Error loading system: {str(e)}")
        return None, None, None


# ===== INITIALIZATION =====
rec_system, anime_df, rating_df = load_recommendation_system()

if rec_system is None:
    st.error("Failed to load recommendation system. Please check the dataset files.")
    st.stop()


# ===== HEADER SECTION =====
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="main-title">🎬 Anime Recommendation System</div>', 
                unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Discover your next favorite anime using AI recommendations</div>',
        unsafe_allow_html=True
    )


# ===== SIDEBAR CONFIGURATION =====
st.sidebar.markdown("## ⚙️ Configuration")
st.sidebar.markdown("---")

# Recommendation Mode Selection
mode = st.sidebar.selectbox(
    label="🎯 Select Recommendation Mode",
    options=["Content-Based", "Collaborative", "Hybrid"],
    help="Choose the recommendation algorithm"
)

st.sidebar.markdown("---")

# Mode-specific inputs
if mode == "Content-Based":
    st.sidebar.markdown("### Content-Based Filtering")
    
    anime_list = rec_system.get_anime_list()
    selected_anime = st.sidebar.selectbox(
        label="📺 Select Anime",
        options=anime_list,
        help="Choose an anime to find similar ones"
    )
    
    top_n = st.sidebar.slider(
        label="📊 Number of Recommendations",
        min_value=5,
        max_value=50,
        value=10,
        step=5
    )
    
    weights_info = "Based on genre similarity (TF-IDF)"

elif mode == "Collaborative":
    st.sidebar.markdown("### Collaborative Filtering (SVD)")
    
    user_id = st.sidebar.number_input(
        label="👤 Enter User ID",
        min_value=1,
        value=1,
        help="Enter a valid user ID from the dataset"
    )
    
    top_n = st.sidebar.slider(
        label="📊 Number of Recommendations",
        min_value=5,
        max_value=50,
        value=10,
        step=5
    )
    
    weights_info = "Based on user rating patterns (SVD matrix factorization)"

else:  # Hybrid
    st.sidebar.markdown("### Hybrid Recommendation")
    
    anime_list = rec_system.get_anime_list()
    selected_anime = st.sidebar.selectbox(
        label="📺 Select Anime",
        options=anime_list,
        help="For content-based component"
    )
    
    user_id = st.sidebar.number_input(
        label="👤 Enter User ID",
        min_value=1,
        value=1,
        help="For collaborative filtering component"
    )
    
    top_n = st.sidebar.slider(
        label="📊 Number of Recommendations",
        min_value=5,
        max_value=50,
        value=10,
        step=5
    )
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        content_weight = st.number_input(
            "Content Weight",
            min_value=0.0,
            max_value=1.0,
            value=0.4,
            step=0.1
        )
    with col2:
        collab_weight = st.number_input(
            "Collab Weight",
            min_value=0.0,
            max_value=1.0,
            value=0.6,
            step=0.1
        )
    
    # Normalize weights
    total_weight = content_weight + collab_weight
    if total_weight > 0:
        content_weight = content_weight / total_weight
        collab_weight = collab_weight / total_weight
    
    weights_info = f"Content: {content_weight:.1%} | Collaborative: {collab_weight:.1%}"

st.sidebar.markdown("---")
st.sidebar.info(f"📌 Algorithm Info: {weights_info}")


# ===== MAIN CONTENT AREA =====
# Create tabs
tab1, tab2, tab3 = st.tabs([
    "🎯 Recommendations",
    "📊 Dataset Explorer",
    "📈 Visualizations"
])


# ===== TAB 1: RECOMMENDATIONS =====
with tab1:
    st.markdown("## 🎯 Get Personalized Recommendations")
    
    # Get recommendations based on selected mode
    if st.button("🚀 Generate Recommendations", use_container_width=True, type="primary"):
        with st.spinner("⏳ Generating recommendations..."):
            if mode == "Content-Based":
                recommendations = rec_system.recommend_content(selected_anime, top_n)
            
            elif mode == "Collaborative":
                recommendations = rec_system.recommend_collaborative(int(user_id), top_n)
            
            else:  # Hybrid
                recommendations = rec_system.recommend_hybrid(
                    selected_anime,
                    int(user_id),
                    top_n,
                    content_weight,
                    collab_weight
                )
        
        # Display results
        st.markdown("---")
        
        if 'error' in recommendations.columns:
            error_msg = recommendations['error'].iloc[0]
            st.error(f"❌ {error_msg}")
        
        elif len(recommendations) == 0:
            st.warning("⚠️ No recommendations found. Try different parameters.")
        
        else:
            st.success(f"✅ Found {len(recommendations)} recommendations!")
            
            # Display as table
            display_recommendations_table(recommendations)
            
            # Display mode info
            if mode == "Content-Based":
                st.info(
                    f"📌 Showing anime similar to **{selected_anime}** based on genres."
                )
            elif mode == "Collaborative":
                st.info(
                    f"📌 Showing anime that users similar to **User {int(user_id)}** rated highly."
                )
            else:
                st.info(
                    f"📌 Showing anime combining genre similarity to **{selected_anime}** "
                    f"and rating patterns from **User {int(user_id)}**."
                )
    
    else:
        st.info("👈 Click the button to generate recommendations")


# ===== TAB 2: DATASET EXPLORER =====
with tab2:
    st.markdown("## 📊 Dataset Explorer")
    
    # Display statistics
    st.markdown("### 📈 Dataset Statistics")
    stats = get_dataset_stats(anime_df, rating_df)
    display_anime_stats(stats)
    
    st.markdown("---")
    
    # Dataset preview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎬 Anime Dataset Preview")
        st.dataframe(
            anime_df[['name', 'genre', 'rating', 'members']].head(10),
            use_container_width=True,
            hide_index=True
        )
        st.caption(f"Total records: {len(anime_df)}")
    
    with col2:
        st.markdown("### ⭐ Ratings Dataset Preview")
        st.dataframe(
            rating_df[['user_id', 'anime_id', 'rating']].head(10),
            use_container_width=True,
            hide_index=True
        )
        st.caption(f"Total records: {len(rating_df)}")
    
    st.markdown("---")
    
    # Filters
    st.markdown("### 🔍 Dataset Filters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Filter by Genre")
        genre_options = get_genre_options(anime_df)
        selected_genre = st.selectbox("Select a genre:", genre_options)
        
        if st.button("📋 Show Anime by Genre", use_container_width=True):
            filtered = rec_system.filter_by_genre(selected_genre, top_n=20)
            st.dataframe(filtered, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### Filter by Rating")
        col_min, col_max = st.columns(2)
        
        with col_min:
            min_rating = st.number_input(
                "Min Rating",
                min_value=0.0,
                max_value=10.0,
                value=7.0,
                step=0.5
            )
        
        with col_max:
            max_rating = st.number_input(
                "Max Rating",
                min_value=0.0,
                max_value=10.0,
                value=10.0,
                step=0.5
            )
        
        if st.button("⭐ Show Anime by Rating", use_container_width=True):
            filtered = rec_system.filter_by_rating(min_rating, max_rating, top_n=20)
            st.dataframe(filtered, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Top anime tables
    st.markdown("### 🏆 Top Anime")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### By Rating")
        top_rated = rec_system.get_top_rated_anime(10)
        st.dataframe(top_rated, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### By Popularity")
        top_popular = rec_system.get_most_popular_anime(10)
        st.dataframe(top_popular, use_container_width=True, hide_index=True)


# ===== TAB 3: VISUALIZATIONS =====
with tab3:
    st.markdown("## 📈 Visualizations & Insights")
    
    # Visualization options
    st.markdown("### 📊 Select Visualizations to Display")
    
    col1, col2 = st.columns(2)
    
    with col1:
        show_top_rated = st.checkbox("Top Anime by Rating", value=True)
        show_popular = st.checkbox("Most Popular Anime", value=True)
    
    with col2:
        show_distribution = st.checkbox("Rating Distribution", value=True)
        show_wordcloud = st.checkbox("Genres WordCloud", value=True)
    
    show_scatter = st.checkbox("Rating vs Popularity Scatter", value=False)
    
    st.markdown("---")
    
    # Display selected visualizations
    viz_cols = st.columns(2)
    viz_idx = 0
    
    if show_top_rated:
        with viz_cols[viz_idx % 2]:
            st.markdown("### 🏆 Top Anime by Rating")
            fig = plot_top_anime_by_rating(anime_df, top_n=10)
            st.pyplot(fig)
        viz_idx += 1
    
    if show_popular:
        with viz_cols[viz_idx % 2]:
            st.markdown("### 📈 Most Popular Anime")
            fig = plot_most_popular_anime(anime_df, top_n=10)
            st.pyplot(fig)
        viz_idx += 1
    
    if show_distribution:
        with viz_cols[viz_idx % 2]:
            st.markdown("### 📊 Rating Distribution")
            fig = plot_rating_distribution(anime_df)
            st.pyplot(fig)
        viz_idx += 1
    
    if show_wordcloud:
        with viz_cols[viz_idx % 2]:
            st.markdown("### 🎨 Genres WordCloud")
            fig = plot_wordcloud_genres(anime_df)
            st.pyplot(fig)
        viz_idx += 1
    
    if show_scatter:
        st.markdown("### 💫 Rating vs Popularity")
        fig = plot_rating_vs_members(anime_df)
        st.pyplot(fig)
    
    st.markdown("---")
    
    # Key insights
    st.markdown("### 💡 Key Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        top_anime_rating = anime_df.loc[anime_df['rating'].idxmax()]
        st.metric(
            "🏅 Highest Rated Anime",
            top_anime_rating['name'],
            f"Rating: {top_anime_rating['rating']:.2f}"
        )
    
    with col2:
        top_anime_members = anime_df.loc[anime_df['members'].idxmax()]
        st.metric(
            "👥 Most Popular Anime",
            top_anime_members['name'],
            f"Members: {format_large_number(top_anime_members['members'])}"
        )
    
    with col3:
        avg_rating = anime_df['rating'].mean()
        st.metric(
            "📊 Average Rating",
            f"{avg_rating:.2f}",
            "Across all anime"
        )


# ===== FOOTER =====
st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.caption("🎬 Anime Recommendation System")

with footer_col2:
    st.caption("Three Modes: Content-Based | Collaborative | Hybrid")

with footer_col3:
    st.caption("Built with Streamlit, Scikit-Learn & TruncatedSVD")


# ===== SESSION STATE & MEMORY OPTIMIZATION =====
if __name__ == "__main__":
    pass
