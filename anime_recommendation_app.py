#!/usr/bin/env python3
"""
Standalone Anime Recommendation System
========================================

Production-ready example using the refactored collaborative filtering model.
No Jupyter required - run directly from command line or Streamlit.

Usage:
    python anime_recommendation_app.py --mode train
    python anime_recommendation_app.py --mode predict --user 1 --anime 5
    python anime_recommendation_app.py --mode recommend --user 1 --top 10

Requirements:
    pandas, numpy, scikit-learn, scipy
    
    Install: pip install -r requirements.txt
"""

import argparse
import pickle
import pandas as pd
import numpy as np
import os
from pathlib import Path
from collaborative_filtering import CollaborativeFilteringModel, batch_predict_ratings


class AnimeRecommendationSystem:
    """
    Complete anime recommendation pipeline combining:
    - Collaborative filtering (using sklearn TruncatedSVD)
    - Content-based filtering (TF-IDF + cosine similarity)
    - Hybrid recommendations (weighted blend)
    """
    
    def __init__(self, model_path='models/cf_model.pkl', 
                 data_path='.', verbose=True):
        """
        Initialize recommendation system.
        
        Parameters
        ----------
        model_path : str
            Path to save/load trained model
        data_path : str
            Path to anime.csv and rating.csv
        verbose : bool
            Print progress messages
        """
        self.model_path = model_path
        self.data_path = data_path
        self.verbose = verbose
        
        self.cf_model = None
        self.anime_data = None
        self.tfidf_matrix = None
        self.cosine_sim = None
        self.indices = None
        
    def log(self, msg):
        """Print if verbose."""
        if self.verbose:
            print(msg)
    
    def load_data(self):
        """Load anime and ratings data."""
        self.log("[1/5] Loading data...")
        
        anime_path = os.path.join(self.data_path, 'anime.csv')
        ratings_path = os.path.join(self.data_path, 'rating.csv')
        
        if not os.path.exists(anime_path) or not os.path.exists(ratings_path):
            raise FileNotFoundError(
                f"Data files not found. Expected:\n"
                f"  {anime_path}\n"
                f"  {ratings_path}"
            )
        
        self.anime_data = pd.read_csv(anime_path)
        ratings_data = pd.read_csv(ratings_path)
        
        self.log(f"  • Anime data: {self.anime_data.shape}")
        self.log(f"  • Ratings data: {ratings_data.shape}")
        
        return ratings_data
    
    def build_content_similarity(self):
        """Build content-based similarity matrix."""
        self.log("[2/5] Building content-based similarity...")
        
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Prepare content features
        self.anime_data['genre'] = self.anime_data['genre'].fillna('Unknown')
        self.anime_data['type'] = self.anime_data['type'].fillna('Unknown')
        self.anime_data['content'] = (
            self.anime_data['genre'].str.replace(', ', ' ') + ' ' + 
            self.anime_data['type']
        )
        
        # TF-IDF
        tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
        self.tfidf_matrix = tfidf.fit_transform(self.anime_data['content'])
        
        # Cosine similarity
        self.cosine_sim = cosine_similarity(self.tfidf_matrix)
        
        # Indices mapping
        self.indices = pd.Series(
            self.anime_data.index, 
            index=self.anime_data['name']
        ).drop_duplicates()
        
        self.log(f"  • Content matrix: {self.tfidf_matrix.shape}")
        self.log(f"  • Similarity matrix: {self.cosine_sim.shape}")
    
    def train_collaborative_model(self, ratings_data):
        """Train collaborative filtering model."""
        self.log("[3/5] Training collaborative filtering model...")
        
        self.cf_model = CollaborativeFilteringModel(
            n_components=10,
            verbose=self.verbose
        )
        self.cf_model.train(ratings_data, test_size=0.2)
        
        return self.cf_model
    
    def save_model(self):
        """Save trained model."""
        self.log(f"[4/5] Saving model to {self.model_path}...")
        
        # Create directory if needed
        Path(self.model_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.cf_model, f)
        
        file_size_mb = os.path.getsize(self.model_path) / (1024 * 1024)
        self.log(f"  ✓ Model saved ({file_size_mb:.2f} MB)")
    
    def load_model(self):
        """Load pre-trained model."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        self.log(f"Loading model from {self.model_path}...")
        with open(self.model_path, 'rb') as f:
            self.cf_model = pickle.load(f)
        
        self.log("  ✓ Model loaded")
    
    def setup(self, train=True):
        """Setup pipeline (load/train model and build similarities)."""
        self.log("=" * 70)
        self.log("ANIME RECOMMENDATION SYSTEM SETUP")
        self.log("=" * 70)
        
        # Load data
        ratings_data = self.load_data()
        
        # Build content similarity
        self.build_content_similarity()
        
        # Load or train collaborative model
        if train or not os.path.exists(self.model_path):
            self.train_collaborative_model(ratings_data)
            self.save_model()
        else:
            self.load_model()
        
        self.log("[5/5] Setup complete!")
        self.log("=" * 70)
    
    def predict_rating(self, user_id, anime_id):
        """Get collaborative filtering prediction."""
        if self.cf_model is None:
            raise RuntimeError("Model not trained. Call setup() first.")
        
        return self.cf_model.predict_rating(user_id, anime_id)
    
    def get_collaborative_recommendations(self, user_id, top_n=10):
        """Get collaborative filtering recommendations."""
        if self.cf_model is None:
            raise RuntimeError("Model not trained. Call setup() first.")
        
        return self.cf_model.get_recommendations(user_id, top_n=top_n)
    
    def get_content_recommendations(self, anime_name, top_n=10):
        """Get content-based recommendations."""
        if self.indices is None:
            raise RuntimeError("Content similarity not built. Call setup() first.")
        
        if anime_name not in self.indices:
            return []
        
        idx = self.indices[anime_name]
        if isinstance(idx, pd.Series):
            idx = idx.iloc[0]
        
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
        
        anime_indices = [i[0] for i in sim_scores]
        return [
            (
                self.anime_data.iloc[idx]['anime_id'],
                self.anime_data.iloc[idx]['name'],
                i[1]
            )
            for idx, i in zip(anime_indices, sim_scores)
        ]
    
    def get_hybrid_recommendations(self, user_id, anime_name, top_n=10, 
                                  collab_weight=0.5):
        """
        Hybrid recommendations combining collaborative + content-based.
        
        Parameters
        ----------
        user_id : int
            User ID for collaborative filtering
        anime_name : str
            Reference anime for content-based filtering
        top_n : int
            Number of recommendations
        collab_weight : float
            Weight for collaborative (0-1). Content weight = 1 - collab_weight
        """
        from sklearn.preprocessing import MinMaxScaler
        
        if anime_name not in self.indices:
            return f"Anime '{anime_name}' not found"
        
        idx = self.indices[anime_name]
        if isinstance(idx, pd.Series):
            idx = idx.iloc[0]
        
        # Content-based candidates
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:100]
        
        anime_indices = [i[0] for i in sim_scores]
        
        results_df = self.anime_data.iloc[anime_indices][
            ['anime_id', 'name', 'genre', 'type']
        ].copy()
        results_df['content_score'] = [i[1] for i in sim_scores]
        
        # Collaborative scores
        collab_preds = [
            self.cf_model.predict_rating(user_id, aid) / 10  # Normalize
            for aid in results_df['anime_id']
        ]
        results_df['collab_score'] = collab_preds
        
        # Normalize both scores
        scaler = MinMaxScaler()
        results_df[['content_score', 'collab_score']] = scaler.fit_transform(
            results_df[['content_score', 'collab_score']]
        )
        
        # Combine scores
        results_df['hybrid_score'] = (
            results_df['collab_score'] * collab_weight +
            results_df['content_score'] * (1 - collab_weight)
        )
        
        return results_df.sort_values('hybrid_score', ascending=False).head(top_n)
    
    def print_model_info(self):
        """Print model information."""
        if self.cf_model is None:
            print("Model not trained")
            return
        
        info = self.cf_model.get_model_info()
        print("\n" + "=" * 70)
        print("MODEL INFORMATION")
        print("=" * 70)
        for key, value in info.items():
            print(f"  {key}: {value}")
        print("=" * 70)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Anime Recommendation System'
    )
    parser.add_argument(
        '--mode',
        choices=['train', 'predict', 'recommend', 'info'],
        default='train',
        help='Operation mode'
    )
    parser.add_argument(
        '--user',
        type=int,
        default=1,
        help='User ID for collaborative filtering'
    )
    parser.add_argument(
        '--anime',
        type=int,
        default=5,
        help='Anime ID for prediction'
    )
    parser.add_argument(
        '--anime-name',
        type=str,
        default='Naruto',
        help='Anime name for content-based recommendations'
    )
    parser.add_argument(
        '--top',
        type=int,
        default=10,
        help='Number of recommendations'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='models/cf_model.pkl',
        help='Path to model file'
    )
    parser.add_argument(
        '--data',
        type=str,
        default='.',
        help='Path to data directory'
    )
    
    args = parser.parse_args()
    
    # Initialize system
    system = AnimeRecommendationSystem(
        model_path=args.model,
        data_path=args.data,
        verbose=True
    )
    
    try:
        if args.mode == 'train':
            # Train from scratch
            system.setup(train=True)
            system.print_model_info()
        
        elif args.mode == 'predict':
            # Load model and predict
            system.load_data()
            system.build_content_similarity()
            system.load_model()
            
            rating = system.predict_rating(args.user, args.anime)
            print(f"\nPredicted rating for User {args.user} → Anime {args.anime}:")
            print(f"  {rating:.2f}/10")
        
        elif args.mode == 'recommend':
            # Load and get recommendations
            system.load_data()
            system.build_content_similarity()
            system.load_model()
            
            recs = system.get_hybrid_recommendations(
                user_id=args.user,
                anime_name=args.anime_name,
                top_n=args.top
            )
            
            print(f"\nTop {args.top} recommendations for User {args.user}:")
            if isinstance(recs, str):
                print(f"  {recs}")
            else:
                print(recs[['name', 'genre', 'hybrid_score']].to_string())
        
        elif args.mode == 'info':
            # Load and show info
            system.load_model()
            system.print_model_info()
    
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == '__main__':
    main()
