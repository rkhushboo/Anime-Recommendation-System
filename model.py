"""
Machine Learning Models for Anime Recommendation System
Supports: Content-Based, Collaborative Filtering (SVD), and Hybrid approaches
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import csr_matrix
import warnings

warnings.filterwarnings('ignore')


class AnimeRecommendationSystem:
    """
    Complete recommendation system supporting three modes:
    1. Content-Based (TF-IDF + Cosine Similarity)
    2. Collaborative Filtering (SVD)
    3. Hybrid (Weighted combination)
    """
    
    def __init__(self, anime_df, rating_df):
        """
        Initialize the recommendation system with datasets
        
        Args:
            anime_df: DataFrame with anime data
            rating_df: DataFrame with user ratings
        """
        self.anime_df = anime_df.reset_index(drop=True)
        self.rating_df = rating_df.reset_index(drop=True)
        
        self.tfidf_matrix = None
        self.svd_model = None
        self.scaler = MinMaxScaler()
        
        # Initialize models
        self._build_tfidf()
        self._train_svd()
    
    def _build_tfidf(self):
        """Build TF-IDF matrix from anime genres"""
        try:
            # Handle missing genres
            genres = self.anime_df['genre'].fillna('Unknown')
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                analyzer='char',
                ngram_range=(2, 3),
                lowercase=True,
                stop_words='english'
            )
            
            self.tfidf_matrix = vectorizer.fit_transform(genres)
            self.vectorizer = vectorizer
            
            print("✓ TF-IDF matrix built successfully")
        except Exception as e:
            print(f"✗ Error building TF-IDF matrix: {e}")
            self.tfidf_matrix = None
    
    def _train_svd(self):
        """Train SVD model on collaborative filtering using sklearn TruncatedSVD"""
        try:
            # Use a sample for faster training if dataset is large
            rating_sample = self.rating_df.copy()
            if len(rating_sample) > 1000000:
                print("  (Large dataset detected - using optimized training)")
                rating_sample = rating_sample.sample(n=500000, random_state=42)
            
            # Drop NaN ratings
            rating_sample = rating_sample.dropna(subset=['rating'])
            
            # Create user-item matrix
            unique_users = rating_sample['user_id'].unique()
            unique_animes = rating_sample['anime_id'].unique()
            
            self.user_id_map = {uid: idx for idx, uid in enumerate(unique_users)}
            self.anime_id_map = {aid: idx for idx, aid in enumerate(unique_animes)}
            
            user_indices = rating_sample['user_id'].map(self.user_id_map).values
            anime_indices = rating_sample['anime_id'].map(self.anime_id_map).values
            ratings = rating_sample['rating'].values
            
            # Build sparse CSR matrix
            user_item_matrix = csr_matrix(
                (ratings, (user_indices, anime_indices)),
                shape=(len(unique_users), len(unique_animes))
            )
            
            self.mean_rating = ratings.mean()
            
            # Convert to dense for SVD (fill zeros with mean rating)
            user_item_dense = user_item_matrix.toarray()
            user_item_dense[user_item_dense == 0] = self.mean_rating
            
            # Train TruncatedSVD model
            self.svd_model = TruncatedSVD(n_components=50, random_state=42)
            self.user_factors = self.svd_model.fit_transform(user_item_dense)
            self.item_factors = self.svd_model.components_.T
            
            # Reconstruct full matrix for predictions
            self.reconstructed_matrix = self.user_factors @ self.item_factors.T
            
            print("✓ SVD model trained successfully")
        except Exception as e:
            print(f"✗ Error training SVD model: {e}")
            self.svd_model = None
    
    def recommend_content(self, anime_name, top_n=10):
        """
        Content-Based Recommendation using TF-IDF + Cosine Similarity
        
        Args:
            anime_name: Name of the anime to base recommendations on
            top_n: Number of recommendations to return
            
        Returns:
            DataFrame with recommendations
        """
        try:
            if self.tfidf_matrix is None:
                return pd.DataFrame({'error': ['TF-IDF model not built']})
            
            # Find anime index
            anime_idx = self.anime_df[
                self.anime_df['name'].str.lower() == anime_name.lower()
            ].index
            
            if len(anime_idx) == 0:
                return pd.DataFrame({'error': [f'Anime "{anime_name}" not found']})
            
            anime_idx = anime_idx[0]
            
            # Compute cosine similarity
            sim_scores = cosine_similarity(
                self.tfidf_matrix[anime_idx],
                self.tfidf_matrix
            )[0]
            
            # Get top similar anime (excluding the anime itself)
            sim_anime_idx = np.argsort(sim_scores)[::-1][1:top_n+1]
            
            recommendations = self.anime_df.iloc[sim_anime_idx].copy()
            recommendations['score'] = sim_scores[sim_anime_idx]
            recommendations['score'] = (recommendations['score'] * 100).round(2)
            
            return recommendations[['name', 'genre', 'rating', 'score']].reset_index(drop=True)
        
        except Exception as e:
            return pd.DataFrame({'error': [f'Content-based error: {str(e)}']})
    
    def recommend_collaborative(self, user_id, top_n=10):
        """
        Collaborative Filtering Recommendation using sklearn TruncatedSVD
        
        Args:
            user_id: User ID to recommend for
            top_n: Number of recommendations to return
            
        Returns:
            DataFrame with recommendations
        """
        try:
            if self.svd_model is None or not hasattr(self, 'user_id_map'):
                return pd.DataFrame({'error': ['SVD model not trained']})
            
            # Check if user exists in dataset
            if user_id not in self.user_id_map:
                return pd.DataFrame({
                    'error': [f'User ID {user_id} not found in dataset']
                })
            
            user_idx = self.user_id_map[user_id]
            
            # Get user's predicted ratings for all anime
            user_ratings = self.reconstructed_matrix[user_idx]
            
            # Get anime already rated by user
            user_rated_mask = self.rating_df['user_id'] == user_id
            user_rated_animes = set(self.rating_df[user_rated_mask]['anime_id'].values)
            
            # Create prediction list for unrated anime
            predictions = []
            for anime_id, anime_idx in self.anime_id_map.items():
                if anime_id not in user_rated_animes:
                    pred_rating = np.clip(user_ratings[anime_idx], 1, 10)
                    predictions.append({
                        'anime_id': anime_id,
                        'predicted_rating': pred_rating
                    })
            
            if not predictions:
                return pd.DataFrame({'error': ['No unrated anime found']})
            
            pred_df = pd.DataFrame(predictions)
            
            # Get top N
            top_anime_ids = pred_df.nlargest(top_n, 'predicted_rating')['anime_id'].values
            
            recommendations = self.anime_df[
                self.anime_df['anime_id'].isin(top_anime_ids)
            ].copy()
            
            # Merge with predictions
            recommendations = recommendations.merge(
                pred_df[pred_df['anime_id'].isin(top_anime_ids)],
                on='anime_id'
            )
            
            recommendations['score'] = (
                recommendations['predicted_rating'] * 20
            ).round(2)  # Scale to 0-100
            
            return recommendations[['name', 'genre', 'rating', 'score']].reset_index(drop=True)
        
        except Exception as e:
            return pd.DataFrame({'error': [f'Collaborative error: {str(e)}']})
    
    def recommend_hybrid(self, anime_name, user_id, top_n=10, 
                        content_weight=0.4, collab_weight=0.6):
        """
        Hybrid Recommendation combining Content-Based and Collaborative
        
        Args:
            anime_name: Anime name for content-based similarity
            user_id: User ID for collaborative filtering
            top_n: Number of recommendations to return
            content_weight: Weight for content-based score (0-1)
            collab_weight: Weight for collaborative score (0-1)
            
        Returns:
            DataFrame with recommendations
        """
        try:
            # Get content-based recommendations
            content_recs = self.recommend_content(anime_name, top_n=top_n*2)
            
            if 'error' in content_recs.columns:
                return content_recs
            
            # Get collaborative recommendations
            collab_recs = self.recommend_collaborative(user_id, top_n=top_n*2)
            
            if 'error' in collab_recs.columns:
                return collab_recs
            
            # Merge recommendations
            merged = pd.merge(
                content_recs,
                collab_recs,
                on='name',
                how='outer',
                suffixes=('_content', '_collab')
            )
            
            # Handle missing scores
            merged['score_content'] = merged['score_content'].fillna(0)
            merged['score_collab'] = merged['score_collab'].fillna(0)
            
            # Normalize scores to 0-100
            merged['score_content'] = (merged['score_content'] / 100)
            merged['score_collab'] = (merged['score_collab'] / 100)
            
            # Weighted combination
            merged['hybrid_score'] = (
                (merged['score_content'] * content_weight) +
                (merged['score_collab'] * collab_weight)
            ) * 100
            
            # Use first available rating
            merged['rating'] = merged['rating_content'].fillna(
                merged['rating_collab']
            )
            merged['genre'] = merged['genre_content'].fillna(
                merged['genre_collab']
            )
            
            # Sort and get top N
            result = merged.nlargest(top_n, 'hybrid_score')
            result['score'] = result['hybrid_score'].round(2)
            
            return result[['name', 'genre', 'rating', 'score']].reset_index(drop=True)
        
        except Exception as e:
            return pd.DataFrame({'error': [f'Hybrid error: {str(e)}']})
    
    def get_anime_list(self):
        """Get list of all anime names for selection"""
        return sorted(self.anime_df['name'].dropna().unique().tolist())
    
    def get_top_rated_anime(self, top_n=10):
        """Get top rated anime"""
        return self.anime_df.nlargest(top_n, 'rating')[
            ['name', 'genre', 'rating', 'members']
        ].reset_index(drop=True)
    
    def get_most_popular_anime(self, top_n=10):
        """Get most popular anime by members"""
        return self.anime_df.nlargest(top_n, 'members')[
            ['name', 'genre', 'rating', 'members']
        ].reset_index(drop=True)
    
    def get_anime_stats(self):
        """Get dataset statistics"""
        return {
            'total_anime': len(self.anime_df),
            'total_users': self.rating_df['user_id'].nunique(),
            'total_ratings': len(self.rating_df),
            'avg_rating': self.anime_df['rating'].mean(),
            'avg_members': self.anime_df['members'].mean(),
        }
    
    def filter_by_genre(self, genre, top_n=10):
        """Filter anime by genre"""
        filtered = self.anime_df[
            self.anime_df['genre'].str.contains(genre, case=False, na=False)
        ].copy()
        return filtered.nlargest(top_n, 'rating')[
            ['name', 'genre', 'rating', 'members']
        ].reset_index(drop=True)
    
    def filter_by_rating(self, min_rating, max_rating, top_n=10):
        """Filter anime by rating range"""
        filtered = self.anime_df[
            (self.anime_df['rating'] >= min_rating) &
            (self.anime_df['rating'] <= max_rating)
        ].copy()
        return filtered.nlargest(top_n, 'members')[
            ['name', 'genre', 'rating', 'members']
        ].reset_index(drop=True)
