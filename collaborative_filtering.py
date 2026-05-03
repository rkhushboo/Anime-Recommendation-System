"""
Collaborative Filtering Module - Production Ready
==================================================

Pure sklearn/pandas/numpy implementation (NO scikit-surprise dependency)
Lightweight, deployable on GitHub & Streamlit Cloud

Author: Refactored for production deployment
Date: 2026
"""

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity


class CollaborativeFilteringModel:
    """
    Lightweight collaborative filtering model using matrix factorization.
    
    Key Features:
    - Uses sklearn's TruncatedSVD instead of Surprise library
    - Memory-efficient sparse matrix operations
    - Streamlit & GitHub deployment ready
    - No external ML dependencies beyond sklearn, pandas, numpy
    
    Usage:
    ------
    model = CollaborativeFilteringModel(n_components=10)
    model.train(ratings_data, test_size=0.2)
    
    # Get prediction for user-anime pair
    pred_rating = model.predict_rating(user_id=1, anime_id=5)
    
    # Get recommendations for user
    recommendations = model.get_recommendations(user_id=1, top_n=10)
    """
    
    def __init__(self, n_components=10, random_state=42, verbose=True):
        """
        Initialize the collaborative filtering model.
        
        Parameters
        ----------
        n_components : int, default=10
            Number of latent factors for matrix factorization.
            Recommended range: 10-20 for balanced performance.
            
        random_state : int, default=42
            Random seed for reproducibility.
            
        verbose : bool, default=True
            Print training progress and metrics.
        """
        self.n_components = n_components
        self.random_state = random_state
        self.verbose = verbose
        
        # Model components
        self.svd_model = TruncatedSVD(
            n_components=n_components, 
            random_state=random_state,
            n_iter=100
        )
        self.user_factors = None
        self.item_factors = None
        self.reconstructed_matrix = None
        self.user_item_matrix = None
        
        # Mappings
        self.user_id_map = None
        self.anime_id_map = None
        self.reverse_user_map = None
        self.reverse_anime_map = None
        
        # Statistics
        self.mean_rating = None
        self.rmse_score = None
        self.test_data = None
        self.training_samples = 0
        
    def preprocess_data(self, ratings_data):
        """
        Preprocess ratings data for training.
        
        Performs:
        1. Filter active users (> 100 interactions)
        2. Drop NaN ratings
        3. Sample to 500k if dataset exceeds this size
        
        Parameters
        ----------
        ratings_data : pd.DataFrame
            DataFrame with columns: ['user_id', 'anime_id', 'rating']
            
        Returns
        -------
        pd.DataFrame
            Cleaned and filtered ratings data
        """
        if self.verbose:
            print("[1/4] Preprocessing data...")
        
        # Step 1: Filter active users
        user_counts = ratings_data['user_id'].value_counts()
        active_users = user_counts[user_counts > 100].index
        ratings_filtered = ratings_data[
            ratings_data['user_id'].isin(active_users)
        ].copy()
        
        if self.verbose:
            print(f"  • Filtered to active users: {len(ratings_filtered):,} "
                  f"ratings from {len(active_users):,} users")
        
        # Step 2: Drop NaN ratings
        ratings_clean = ratings_filtered.dropna(subset=['rating']).copy()
        
        if self.verbose:
            print(f"  • Removed NaN ratings: {len(ratings_clean):,} remain")
        
        # Step 3: Sample for memory efficiency
        if len(ratings_clean) > 500000:
            ratings_clean = ratings_clean.sample(n=500000, random_state=42)
            if self.verbose:
                print(f"  • Sampled to 500k: {len(ratings_clean):,} "
                      "for training")
        
        return ratings_clean
    
    def build_user_item_matrix(self, ratings_data):
        """
        Build sparse user-item matrix from ratings.
        
        Parameters
        ----------
        ratings_data : pd.DataFrame
            Cleaned ratings DataFrame
            
        Returns
        -------
        scipy.sparse.csr_matrix
            User-item interaction matrix (sparse)
        """
        if self.verbose:
            print("[2/4] Building user-item matrix...")
        
        # Create ID mappings
        unique_users = ratings_data['user_id'].unique()
        unique_animes = ratings_data['anime_id'].unique()
        
        self.user_id_map = {uid: idx for idx, uid in enumerate(unique_users)}
        self.anime_id_map = {aid: idx for idx, aid in enumerate(unique_animes)}
        
        # Create reverse mappings
        self.reverse_user_map = {v: k for k, v in self.user_id_map.items()}
        self.reverse_anime_map = {v: k for k, v in self.anime_id_map.items()}
        
        # Map ratings to matrix indices
        user_indices = ratings_data['user_id'].map(self.user_id_map).values
        anime_indices = ratings_data['anime_id'].map(self.anime_id_map).values
        ratings = ratings_data['rating'].values
        
        # Build sparse CSR matrix (memory efficient)
        self.user_item_matrix = csr_matrix(
            (ratings, (user_indices, anime_indices)),
            shape=(len(unique_users), len(unique_animes))
        )
        
        # Compute statistics
        self.mean_rating = ratings_data['rating'].mean()
        sparsity = 1 - (len(ratings) / (len(unique_users) * len(unique_animes)))
        
        if self.verbose:
            print(f"  • Matrix shape: {self.user_item_matrix.shape} "
                  "(users × anime)")
            print(f"  • Sparsity: {sparsity*100:.2f}%")
            print(f"  • Mean rating: {self.mean_rating:.2f}")
        
        return self.user_item_matrix
    
    def train(self, ratings_data, test_size=0.2):
        """
        Train the collaborative filtering model.
        
        Full pipeline:
        1. Preprocess data (filter, clean, sample)
        2. Split train/test
        3. Build user-item matrix
        4. Apply TruncatedSVD
        5. Evaluate on test set
        
        Parameters
        ----------
        ratings_data : pd.DataFrame
            Raw ratings with ['user_id', 'anime_id', 'rating']
            
        test_size : float, default=0.2
            Fraction of data for evaluation (0.2 = 20%)
        """
        if self.verbose:
            print("=" * 70)
            print("COLLABORATIVE FILTERING - TRAINING")
            print("=" * 70)
        
        # Preprocess
        ratings_clean = self.preprocess_data(ratings_data)
        
        # Train/test split
        if self.verbose:
            print(f"  • Train/test split: {int((1-test_size)*100)}% / "
                  f"{int(test_size*100)}%")
        
        test_indices = np.random.RandomState(42).choice(
            len(ratings_clean),
            size=int(len(ratings_clean) * test_size),
            replace=False
        )
        train_mask = np.ones(len(ratings_clean), dtype=bool)
        train_mask[test_indices] = False
        
        ratings_train = ratings_clean[train_mask].copy()
        self.test_data = ratings_clean[~train_mask].copy()
        self.training_samples = len(ratings_train)
        
        # Build matrix
        self.build_user_item_matrix(ratings_train)
        
        # Train SVD
        if self.verbose:
            print("[3/4] Training TruncatedSVD model...")
        
        user_item_dense = self.user_item_matrix.toarray()
        user_item_dense[user_item_dense == 0] = self.mean_rating
        
        self.svd_model.fit(user_item_dense)
        
        if self.verbose:
            print(f"  • SVD fitted with {self.n_components} components")
        
        # Get factors
        self.user_factors = self.svd_model.transform(user_item_dense)
        self.item_factors = self.svd_model.components_.T
        
        if self.verbose:
            print(f"  • User factors shape: {self.user_factors.shape}")
            print(f"  • Item factors shape: {self.item_factors.shape}")
        
        # Reconstruct matrix
        self.reconstructed_matrix = self.user_factors @ self.item_factors.T
        
        # Evaluate
        self._evaluate()
        
        if self.verbose:
            print("\n" + "=" * 70)
            print("✓ Model training complete!")
            print("=" * 70)
    
    def _evaluate(self):
        """Compute RMSE on test set."""
        if self.verbose:
            print("[4/4] Evaluating model...")
        
        if self.test_data is None or len(self.test_data) == 0:
            if self.verbose:
                print("  ⚠️  No test data for evaluation")
            return
        
        predictions = []
        actuals = []
        
        for _, row in self.test_data.iterrows():
            user_id = row['user_id']
            anime_id = row['anime_id']
            actual = row['rating']
            
            if user_id not in self.user_id_map or anime_id not in self.anime_id_map:
                continue
            
            user_idx = self.user_id_map[user_id]
            anime_idx = self.anime_id_map[anime_id]
            pred = self.reconstructed_matrix[user_idx, anime_idx]
            
            predictions.append(pred)
            actuals.append(actual)
        
        if len(predictions) > 0:
            rmse = np.sqrt(np.mean((np.array(predictions) - 
                                   np.array(actuals)) ** 2))
            self.rmse_score = rmse
            
            if self.verbose:
                print(f"  ✓ RMSE: {rmse:.4f}")
                print(f"  ✓ Evaluated on {len(predictions):,} test ratings")
        else:
            if self.verbose:
                print("  ⚠️  Could not evaluate (no valid test samples)")
    
    def predict_rating(self, user_id, anime_id):
        """
        Predict rating for a user-anime pair.
        
        Parameters
        ----------
        user_id : int
            User ID
            
        anime_id : int
            Anime ID
            
        Returns
        -------
        float
            Predicted rating (1-10 scale, clipped)
        """
        if user_id not in self.user_id_map or anime_id not in self.anime_id_map:
            return self.mean_rating
        
        user_idx = self.user_id_map[user_id]
        anime_idx = self.anime_id_map[anime_id]
        pred = self.reconstructed_matrix[user_idx, anime_idx]
        
        return np.clip(pred, 1, 10)
    
    def get_recommendations(self, user_id, exclude_anime=None, top_n=10):
        """
        Get top-N anime recommendations for a user.
        
        Parameters
        ----------
        user_id : int
            User ID
            
        exclude_anime : list, optional
            Anime IDs to exclude (already watched). Default: None
            
        top_n : int, default=10
            Number of recommendations to return
            
        Returns
        -------
        list of tuples
            [(anime_id, predicted_rating), ...] sorted by rating (desc)
        """
        if user_id not in self.user_id_map:
            return []
        
        if exclude_anime is None:
            exclude_anime = []
        
        user_idx = self.user_id_map[user_id]
        user_ratings = self.reconstructed_matrix[user_idx]
        
        # Get unwatched anime
        all_animes = list(self.anime_id_map.values())
        watched = {
            self.anime_id_map[aid] for aid in exclude_anime 
            if aid in self.anime_id_map
        }
        candidates = [idx for idx in all_animes if idx not in watched]
        
        # Get top predictions
        candidate_ratings = user_ratings[candidates]
        top_indices = np.argsort(candidate_ratings)[-top_n:][::-1]
        
        recommendations = [
            (self.reverse_anime_map[candidates[idx]], 
             user_ratings[candidates[idx]])
            for idx in top_indices
        ]
        
        return recommendations
    
    def get_similar_items(self, anime_id, top_n=10):
        """
        Get anime similar to a given anime using item factors.
        
        Parameters
        ----------
        anime_id : int
            Anime ID
            
        top_n : int, default=10
            Number of similar items
            
        Returns
        -------
        list of tuples
            [(anime_id, similarity_score), ...]
        """
        if anime_id not in self.anime_id_map:
            return []
        
        anime_idx = self.anime_id_map[anime_id]
        item_vector = self.item_factors[anime_idx].reshape(1, -1)
        
        # Cosine similarity
        similarities = cosine_similarity(item_vector, self.item_factors)[0]
        
        # Top similar (exclude self)
        top_indices = np.argsort(similarities)[-top_n-1:-1][::-1]
        
        similar = [
            (self.reverse_anime_map[idx], similarities[idx])
            for idx in top_indices
        ]
        
        return similar
    
    def get_model_info(self):
        """Return model information and statistics."""
        info = {
            'n_components': self.n_components,
            'n_users': len(self.user_id_map) if self.user_id_map else 0,
            'n_items': len(self.anime_id_map) if self.anime_id_map else 0,
            'training_samples': self.training_samples,
            'mean_rating': self.mean_rating,
            'rmse': self.rmse_score,
            'user_factors_shape': self.user_factors.shape if self.user_factors is not None else None,
            'item_factors_shape': self.item_factors.shape if self.item_factors is not None else None,
        }
        return info
    
    def __repr__(self):
        """String representation of model."""
        info = self.get_model_info()
        return (
            f"CollaborativeFilteringModel("
            f"n_users={info['n_users']}, "
            f"n_items={info['n_items']}, "
            f"n_components={info['n_components']}, "
            f"rmse={info['rmse']:.4f if info['rmse'] else 'N/A'})"
        )


# ============================================================================
# CONVENIENCE FUNCTIONS FOR STREAMLIT INTEGRATION
# ============================================================================

def create_and_train_model(ratings_df, n_components=10, test_size=0.2, verbose=True):
    """
    Create and train a collaborative filtering model in one step.
    
    Parameters
    ----------
    ratings_df : pd.DataFrame
        Ratings data with ['user_id', 'anime_id', 'rating']
    
    n_components : int
        Number of latent factors
    
    test_size : float
        Test fraction
    
    verbose : bool
        Print progress
        
    Returns
    -------
    CollaborativeFilteringModel
        Trained model
    """
    model = CollaborativeFilteringModel(
        n_components=n_components, 
        verbose=verbose
    )
    model.train(ratings_df, test_size=test_size)
    return model


def batch_predict_ratings(model, user_anime_pairs):
    """
    Get predictions for multiple user-anime pairs.
    
    Parameters
    ----------
    model : CollaborativeFilteringModel
        Trained model
    
    user_anime_pairs : list of tuples
        [(user_id, anime_id), ...]
        
    Returns
    -------
    list
        Predicted ratings
    """
    predictions = []
    for user_id, anime_id in user_anime_pairs:
        pred = model.predict_rating(user_id, anime_id)
        predictions.append(pred)
    return predictions


if __name__ == "__main__":
    # Example usage
    print("Collaborative Filtering Module")
    print("=" * 70)
    print("Import this module and use:")
    print("  model = CollaborativeFilteringModel(n_components=10)")
    print("  model.train(ratings_data, test_size=0.2)")
    print("  prediction = model.predict_rating(user_id=1, anime_id=5)")
    print("  recommendations = model.get_recommendations(user_id=1, top_n=10)")
    print("=" * 70)
