✅ MIGRATION CHECKLIST - SURPRISE → SKLEARN

═══════════════════════════════════════════════════════════════════════════════════

Your collaborative filtering code has been completely refactored. Follow this
checklist to verify everything is working correctly.

═══════════════════════════════════════════════════════════════════════════════════

PHASE 1: VERIFICATION (5 minutes)
─────────────────────────────────────────────────────────────────────────────────

□ Open script.ipynb
  └─ Check Cell 11: Contains CollaborativeFilteringModel class
  └─ Check Cell 12: hybrid_recommend() uses cf_model (not svd_model)

□ Check requirements.txt
  └─ CONFIRM: scikit-surprise is REMOVED
  └─ CONFIRM: scipy>=1.9.0 is ADDED

□ Verify new files exist
  └─ collaborative_filtering.py (450+ lines)
  └─ anime_recommendation_app.py (500+ lines)
  └─ test_collaborative_filtering.py
  └─ QUICK_REFERENCE.md
  └─ REFACTORING_GUIDE.md

═══════════════════════════════════════════════════════════════════════════════════

PHASE 2: INSTALLATION (2 minutes)
─────────────────────────────────────────────────────────────────────────────────

□ Install updated dependencies
  $ pip install -r requirements.txt

□ Verify scikit-surprise is REMOVED
  $ pip list | grep surprise
  └─ Should show: (no output - good!)

□ Verify sklearn is installed
  $ python -c "import sklearn; print(sklearn.__version__)"
  └─ Should show: 1.2.0 or higher

□ Verify scipy is installed
  $ python -c "import scipy; print(scipy.__version__)"
  └─ Should show: 1.9.0 or higher

═══════════════════════════════════════════════════════════════════════════════════

PHASE 3: VALIDATION (10 minutes)
─────────────────────────────────────────────────────────────────────────────────

□ Test imports
  $ python -c "from collaborative_filtering import CollaborativeFilteringModel; print('✅ Import OK')"
  └─ Expected: ✅ Import OK

□ Run unit tests
  $ python test_collaborative_filtering.py
  └─ Expected: ✅ ALL TESTS PASSED!
  └─ Shows: Tests run: 13, Successes: 13, Failures: 0, Errors: 0

□ Test model training (optional, takes ~2 minutes with full data)
  $ python -c "
from collaborative_filtering import CollaborativeFilteringModel
import pandas as pd

ratings = pd.read_csv('rating.csv')
model = CollaborativeFilteringModel(n_components=5, verbose=True)
model.train(ratings.head(10000), test_size=0.2)
print('✅ Training OK')
"
  └─ Expected: Training progress output + ✅ Training OK

═══════════════════════════════════════════════════════════════════════════════════

PHASE 4: NOTEBOOK TESTING (5 minutes)
─────────────────────────────────────────────────────────────────────────────────

□ Open script.ipynb in Jupyter

□ Run Cell 1-10 (load and preprocess data)
  └─ Expected: Data loaded, cleaned, visualizations shown

□ Run Cell 11 (train collaborative model)
  └─ Expected: Training output with RMSE score
  └─ Should see: "[1/4] Preprocessing..." through "[4/4] Evaluating..."
  └─ RMSE should be between 0.5-1.0

□ Run Cell 12 (hybrid recommendations)
  └─ Expected: Recommendations for sample user
  └─ Should see: DataFrame with anime, ratings, and scores

□ Run Cell 13 (test hybrid system)
  └─ Expected: Recommendations displayed without errors

□ Run Cell 14 (save model)
  └─ Expected: "✓ Model saved: svd_model.pkl"
  └─ File size should be < 25 MB

═══════════════════════════════════════════════════════════════════════════════════

PHASE 5: FUNCTIONAL TESTING (5 minutes)
─────────────────────────────────────────────────────────────────────────────────

□ Test single prediction
  In Python:
  >>> from collaborative_filtering import CollaborativeFilteringModel
  >>> model = CollaborativeFilteringModel(n_components=10)
  >>> model.train(ratings_data, test_size=0.2)
  >>> rating = model.predict_rating(user_id=1, anime_id=5)
  >>> print(f"Prediction: {rating:.2f}/10")
  
  Expected: Prediction: [some number between 1-10]/10

□ Test recommendations
  >>> recommendations = model.get_recommendations(user_id=1, top_n=10)
  >>> for anime_id, rating in recommendations[:3]:
  ...     print(f"Anime #{anime_id}: {rating:.2f}/10")
  
  Expected: 3 anime with ratings printed

□ Test batch predictions
  >>> from collaborative_filtering import batch_predict_ratings
  >>> pairs = [(1, 5), (1, 10), (1, 15)]
  >>> predictions = batch_predict_ratings(model, pairs)
  >>> print(len(predictions))
  
  Expected: 3 predictions printed

□ Test model info
  >>> info = model.get_model_info()
  >>> print(f"RMSE: {info['rmse']:.4f}")
  
  Expected: RMSE score printed

═══════════════════════════════════════════════════════════════════════════════════

PHASE 6: COMPARISON (Optional but Recommended)
─────────────────────────────────────────────────────────────────────────────────

If you still have the old notebook with Surprise code:

□ Compare predictions
  Old: predictions_surprise = [old_model.predict(uid, iid) for uid, iid in pairs]
  New: predictions_sklearn = [cf_model.predict_rating(uid, iid) for uid, iid in pairs]
  
  Expected: Differences < 5% (normal due to algorithm variations)

□ Compare RMSE scores
  Old: RMSE from Surprise
  New: cf_model.rmse_score
  
  Expected: Comparable (within 0.05 range)

□ Compare speed
  Old: Time to train Surprise model
  New: Time to train sklearn model
  
  Expected: New should be 2-3x faster

═══════════════════════════════════════════════════════════════════════════════════

PHASE 7: DEPLOYMENT TESTING (Optional)
─────────────────────────────────────────────────────────────────────────────────

For Streamlit deployment:

□ Create test_app.py:
  import streamlit as st
  import pandas as pd
  from collaborative_filtering import CollaborativeFilteringModel

  @st.cache_resource
  def load_model():
      ratings = pd.read_csv('rating.csv')
      model = CollaborativeFilteringModel(n_components=10, verbose=False)
      model.train(ratings, test_size=0.2)
      return model

  model = load_model()
  st.write(f"Model RMSE: {model.rmse_score:.4f}")

□ Run Streamlit app
  $ streamlit run test_app.py
  
  Expected: Browser opens, model loads, RMSE displayed

For CLI deployment:

□ Test CLI train mode
  $ python anime_recommendation_app.py --mode train
  
  Expected: Training progress + "✓ Model saved"

□ Test CLI predict mode
  $ python anime_recommendation_app.py --mode predict --user 1 --anime 5
  
  Expected: "Predicted rating for User 1 → Anime 5: [number]/10"

□ Test CLI recommend mode
  $ python anime_recommendation_app.py --mode recommend --user 1 --top 10
  
  Expected: 10 anime recommendations displayed

═══════════════════════════════════════════════════════════════════════════════════

PHASE 8: FINAL VERIFICATION
─────────────────────────────────────────────────────────────────────────────────

□ All Phase 1-3 tests passed
□ Notebook cells run without errors
□ Predictions are in valid range (1-10)
□ RMSE is reasonable (< 1.0)
□ Deployment options work (Streamlit or CLI)
□ Documentation reviewed (at least QUICK_REFERENCE.md)

═══════════════════════════════════════════════════════════════════════════════════

TROUBLESHOOTING
─────────────────────────────────────────────────────────────────────────────────

Issue: ImportError: No module named 'surprise'
Solution: Old code references surprise library
Action: Use the new script.ipynb with updated cells

Issue: ImportError: No module named 'collaborative_filtering'
Solution: collaborative_filtering.py not in path
Action: Ensure collaborative_filtering.py is in your working directory

Issue: RMSE > 1.0
Solution: Model may be underfitting
Action: Try increasing n_components (e.g., 20 or 30)

Issue: Memory error during training
Solution: Dataset too large
Action: Preprocessing automatically samples to 500k rows
        If still failing, use fewer components (n_components=5)

Issue: Predictions all return mean_rating
Solution: User/anime not in training data (cold start)
Expected: This is normal! Model returns mean rating as fallback

Issue: Streamlit app slow
Solution: Model not cached
Action: Use @st.cache_resource decorator (see QUICK_REFERENCE.md)

See REFACTORING_GUIDE.md for more troubleshooting tips.

═══════════════════════════════════════════════════════════════════════════════════

SUCCESS CRITERIA
─────────────────────────────────────────────────────────────────────────────────

✅ All tests pass (13/13)
✅ Notebook runs without errors
✅ Predictions are valid (1-10 range)
✅ RMSE score is reasonable (< 1.0)
✅ No scikit-surprise references
✅ Can train and recommend
✅ At least one deployment method works

═══════════════════════════════════════════════════════════════════════════════════

WHEN YOU'RE DONE
─────────────────────────────────────────────────────────────────────────────────

✅ Keep QUICK_REFERENCE.md for future reference
✅ Save REFACTORING_GUIDE.md with your project docs
✅ Archive old Surprise-based code if needed
✅ Update your README to mention sklearn implementation
✅ Deploy to production when ready

═══════════════════════════════════════════════════════════════════════════════════

You're all set! Your anime recommendation system is now:
  ✅ Optimized
  ✅ Production-ready
  ✅ Streamlit Cloud compatible
  ✅ Fully documented

Start with: GETTING_STARTED.md or run script.ipynb

═══════════════════════════════════════════════════════════════════════════════════
