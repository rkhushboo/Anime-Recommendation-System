#!/usr/bin/env python3
"""
Test Suite for Collaborative Filtering Model
==============================================

Validates that the refactored model works correctly.
Includes unit tests for all major functions.

Usage:
    python test_collaborative_filtering.py

Requires:
    pandas, numpy, scikit-learn, scipy
"""

import unittest
import pandas as pd
import numpy as np
from io import StringIO
import sys
import warnings

warnings.filterwarnings('ignore')

# Import the model
try:
    from collaborative_filtering import (
        CollaborativeFilteringModel,
        batch_predict_ratings
    )
except ImportError:
    print("Error: collaborative_filtering.py not found")
    sys.exit(1)


class TestCollaborativeFilteringModel(unittest.TestCase):
    """Unit tests for CollaborativeFilteringModel."""
    
    @classmethod
    def setUpClass(cls):
        """Create synthetic test data."""
        np.random.seed(42)
        
        # Synthetic ratings: 100 users, 50 anime, ~2000 ratings
        n_users = 100
        n_anime = 50
        n_ratings = 2000
        
        user_ids = np.random.choice(range(1, n_users + 1), n_ratings)
        anime_ids = np.random.choice(range(1, n_anime + 1), n_ratings)
        ratings = np.random.uniform(1, 10, n_ratings)
        
        # Make some users very active (> 100 ratings) for filtering
        active_users = list(range(1, 21))  # First 20 users are "active"
        for i in range(200):
            user_ids = np.append(user_ids, np.random.choice(active_users))
            anime_ids = np.append(anime_ids, np.random.choice(range(1, n_anime + 1)))
            ratings = np.append(ratings, np.random.uniform(1, 10, 1))
        
        cls.ratings_df = pd.DataFrame({
            'user_id': user_ids,
            'anime_id': anime_ids,
            'rating': ratings
        })
    
    def test_initialization(self):
        """Test model initialization."""
        model = CollaborativeFilteringModel(n_components=5, verbose=False)
        self.assertEqual(model.n_components, 5)
        self.assertIsNone(model.user_factors)
        self.assertIsNone(model.item_factors)
    
    def test_preprocess_data(self):
        """Test data preprocessing."""
        model = CollaborativeFilteringModel(verbose=False)
        processed = model.preprocess_data(self.ratings_df)
        
        # Check that data is cleaned
        self.assertGreater(len(processed), 0)
        self.assertFalse(processed['rating'].isna().any())
    
    def test_build_user_item_matrix(self):
        """Test matrix building."""
        model = CollaborativeFilteringModel(verbose=False)
        ratings_clean = model.preprocess_data(self.ratings_df)
        matrix = model.build_user_item_matrix(ratings_clean)
        
        # Check matrix properties
        self.assertGreater(matrix.shape[0], 0)
        self.assertGreater(matrix.shape[1], 0)
        self.assertTrue(hasattr(matrix, 'toarray'))  # Is sparse matrix
    
    def test_train(self):
        """Test model training."""
        model = CollaborativeFilteringModel(n_components=5, verbose=False)
        model.train(self.ratings_df, test_size=0.2)
        
        # Check training results
        self.assertIsNotNone(model.user_factors)
        self.assertIsNotNone(model.item_factors)
        self.assertIsNotNone(model.rmse_score)
        self.assertGreater(model.rmse_score, 0)
        self.assertLess(model.rmse_score, 5)  # Should be reasonable
    
    def test_predict_rating(self):
        """Test rating prediction."""
        model = CollaborativeFilteringModel(n_components=5, verbose=False)
        model.train(self.ratings_df, test_size=0.2)
        
        # Predict for trained user/item
        user_id = list(model.user_id_map.keys())[0]
        anime_id = list(model.anime_id_map.keys())[0]
        prediction = model.predict_rating(user_id, anime_id)
        
        # Check prediction properties
        self.assertIsInstance(prediction, (float, np.floating))
        self.assertGreaterEqual(prediction, 1)
        self.assertLessEqual(prediction, 10)
    
    def test_predict_unknown_user(self):
        """Test prediction for unknown user (cold start)."""
        model = CollaborativeFilteringModel(n_components=5, verbose=False)
        model.train(self.ratings_df, test_size=0.2)
        
        # Unknown user should return mean rating
        unknown_user = 999999
        anime_id = list(model.anime_id_map.keys())[0]
        prediction = model.predict_rating(unknown_user, anime_id)
        
        self.assertAlmostEqual(prediction, model.mean_rating)
    
    def test_get_recommendations(self):
        """Test getting recommendations."""
        model = CollaborativeFilteringModel(n_components=5, verbose=False)
        model.train(self.ratings_df, test_size=0.2)
        
        # Get recommendations
        user_id = list(model.user_id_map.keys())[0]
        recommendations = model.get_recommendations(user_id, top_n=5)
        
        # Check recommendations
        self.assertEqual(len(recommendations), 5)
        for anime_id, rating in recommendations:
            self.assertGreaterEqual(rating, 1)
            self.assertLessEqual(rating, 10)
    
    def test_get_similar_items(self):
        """Test getting similar items."""
        model = CollaborativeFilteringModel(n_components=5, verbose=False)
        model.train(self.ratings_df, test_size=0.2)
        
        # Get similar items
        anime_id = list(model.anime_id_map.keys())[0]
        similar = model.get_similar_items(anime_id, top_n=5)
        
        # Check results
        self.assertGreater(len(similar), 0)
        for sim_anime_id, similarity_score in similar:
            self.assertGreaterEqual(similarity_score, 0)
            self.assertLessEqual(similarity_score, 1)
    
    def test_get_model_info(self):
        """Test getting model information."""
        model = CollaborativeFilteringModel(n_components=5, verbose=False)
        model.train(self.ratings_df, test_size=0.2)
        
        info = model.get_model_info()
        
        # Check info contents
        self.assertIn('n_components', info)
        self.assertIn('n_users', info)
        self.assertIn('n_items', info)
        self.assertIn('rmse', info)
        self.assertEqual(info['n_components'], 5)
    
    def test_batch_predict_ratings(self):
        """Test batch predictions."""
        model = CollaborativeFilteringModel(n_components=5, verbose=False)
        model.train(self.ratings_df, test_size=0.2)
        
        # Create pairs
        user_ids = [list(model.user_id_map.keys())[0]] * 5
        anime_ids = list(model.anime_id_map.keys())[:5]
        pairs = list(zip(user_ids, anime_ids))
        
        # Batch predict
        predictions = batch_predict_ratings(model, pairs)
        
        # Check results
        self.assertEqual(len(predictions), 5)
        for pred in predictions:
            self.assertGreaterEqual(pred, 1)
            self.assertLessEqual(pred, 10)
    
    def test_model_repr(self):
        """Test model string representation."""
        model = CollaborativeFilteringModel(n_components=5, verbose=False)
        model.train(self.ratings_df, test_size=0.2)
        
        repr_str = repr(model)
        
        # Check that key info is in repr
        self.assertIn('CollaborativeFilteringModel', repr_str)
        self.assertIn('n_components', repr_str)
    
    def test_deterministic_results(self):
        """Test that results are reproducible."""
        # Train two models with same seed
        model1 = CollaborativeFilteringModel(n_components=5, random_state=42, verbose=False)
        model1.train(self.ratings_df, test_size=0.2)
        pred1 = model1.predict_rating(
            list(model1.user_id_map.keys())[0],
            list(model1.anime_id_map.keys())[0]
        )
        
        model2 = CollaborativeFilteringModel(n_components=5, random_state=42, verbose=False)
        model2.train(self.ratings_df, test_size=0.2)
        pred2 = model2.predict_rating(
            list(model2.user_id_map.keys())[0],
            list(model2.anime_id_map.keys())[0]
        )
        
        # Predictions should be identical
        self.assertAlmostEqual(pred1, pred2, places=5)


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    @classmethod
    def setUpClass(cls):
        """Create test data."""
        np.random.seed(42)
        
        # More realistic synthetic data
        n_users = 500
        n_anime = 100
        n_ratings = 5000
        
        user_ids = np.random.choice(range(1, n_users + 1), n_ratings)
        anime_ids = np.random.choice(range(1, n_anime + 1), n_ratings)
        ratings = np.random.uniform(1, 10, n_ratings)
        
        # Add active users
        active_users = list(range(1, 51))
        for i in range(1000):
            user_ids = np.append(user_ids, np.random.choice(active_users))
            anime_ids = np.append(anime_ids, np.random.choice(range(1, n_anime + 1)))
            ratings = np.append(ratings, np.random.uniform(1, 10, 1))
        
        cls.ratings_df = pd.DataFrame({
            'user_id': user_ids,
            'anime_id': anime_ids,
            'rating': ratings
        })
    
    def test_full_pipeline(self):
        """Test full recommendation pipeline."""
        model = CollaborativeFilteringModel(n_components=10, verbose=False)
        model.train(self.ratings_df, test_size=0.2)
        
        # Get a trained user
        user_id = list(model.user_id_map.keys())[0]
        
        # Test all APIs
        pred = model.predict_rating(user_id, 5)
        self.assertIsNotNone(pred)
        
        recs = model.get_recommendations(user_id, top_n=10)
        self.assertEqual(len(recs), 10)
        
        info = model.get_model_info()
        self.assertIsNotNone(info)


def run_tests():
    """Run all tests."""
    print("=" * 70)
    print("TESTING COLLABORATIVE FILTERING MODEL")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestCollaborativeFilteringModel))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
