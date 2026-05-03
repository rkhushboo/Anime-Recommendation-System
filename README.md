# 🎬 Anime Recommendation System

A professional, interactive Streamlit web application for recommending anime using three different approaches: **Content-Based**, **Collaborative Filtering**, and **Hybrid** recommendations.

## ✨ Features

### 🎯 Three Recommendation Modes

1. **Content-Based Filtering**
   - Uses TF-IDF on anime genres
   - Finds anime similar to your selection
   - Fast and deterministic
   
2. **Collaborative Filtering (SVD)**
   - Uses Matrix Factorization with SVD
   - Recommends based on user rating patterns
   - Finds anime liked by similar users
   
3. **Hybrid Recommendation**
   - Combines both methods
   - Customizable weight distribution
   - Best of both worlds

### 📊 Dataset Explorer
- Preview anime and rating datasets
- View comprehensive statistics
- Filter by genre and rating range
- Explore top anime by rating and popularity

### 📈 Visualization & Insights
- Top anime by rating (bar chart)
- Most popular anime (members)
- Rating distribution
- Genre word cloud
- Rating vs Popularity scatter plot
- Key metrics and insights

## 🛠️ Technical Stack

- **Framework**: Streamlit
- **ML Libraries**: scikit-learn, scikit-surprise
- **Data Processing**: pandas, numpy
- **Visualization**: matplotlib, seaborn, plotly, wordcloud
- **Python Version**: 3.12+

## 📋 Project Structure

```
Anime_Recommendation/
├── app.py                 # Main Streamlit UI application
├── model.py              # Machine Learning models and logic
├── utils.py              # Helper functions for data & visualization
├── test_system.py        # Test script to verify the system
├── requirements.txt      # Python dependencies
├── anime.csv             # Anime dataset
├── rating.csv            # User ratings dataset
└── README.md             # This file
```

## 🚀 Installation

### 1. Clone/Navigate to the project directory
```bash
cd "c:\Users\richi\DATA SCIENCE - IIT GUWAHATI\DEPLOYMENT\Anime_Recommendation"
```

### 2. Create a Python environment (optional but recommended)
```bash
# Using conda
conda create -n anime_rec python=3.12
conda activate anime_rec

# Or using venv
python -m venv anime_env
anime_env\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## 📖 Usage Guide

### Getting Recommendations

#### Content-Based Mode
1. Select "Content-Based" from the sidebar
2. Choose an anime you like
3. Set the number of recommendations (5-50)
4. Click "Generate Recommendations"
5. View similar anime based on genres

#### Collaborative Mode
1. Select "Collaborative" from the sidebar
2. Enter a valid user ID (e.g., 1, 5, 100)
3. Set the number of recommendations
4. Click "Generate Recommendations"
5. Get personalized suggestions based on rating patterns

#### Hybrid Mode
1. Select "Hybrid" from the sidebar
2. Choose a reference anime
3. Enter a user ID
4. Adjust the content/collaborative weights if desired
5. Click "Generate Recommendations"
6. Get balanced recommendations

### Exploring the Dataset
- **Dataset Explorer Tab**: Browse anime, ratings, and statistics
- **Filters**: Find anime by genre or rating range
- **Top Anime**: See the best and most popular anime

### Visualizations
- **Recommendations Tab**: Generated recommendations table
- **Dataset Explorer Tab**: Statistics and filters
- **Visualizations Tab**: Charts, word clouds, and insights

## 📊 Dataset Information

### anime.csv
- **anime_id**: Unique identifier
- **name**: Anime title
- **genre**: Comma-separated genres
- **rating**: Average rating (0-10)
- **members**: Number of community members
- Other metadata fields

### rating.csv
- **user_id**: Unique user identifier
- **anime_id**: Anime identifier
- **rating**: User's rating (1-10, -1 = not watched)

## 🔧 Configuration

### Recommendation Parameters
- **Top N**: Number of recommendations to display (5-50)
- **Content Weight**: Importance of genre similarity (0-1)
- **Collaborative Weight**: Importance of user patterns (0-1)

### Model Hyperparameters (in model.py)
- **TF-IDF**: char n-grams (2,3), English stop words
- **SVD**: 100 factors, 20 epochs, random_state=42

## 🧪 Testing

Run the test script to verify all components:

```bash
python test_system.py
```

This will:
- ✓ Verify all imports
- ✓ Test data loading and cleaning
- ✓ Initialize the recommendation system
- ✓ Test all three recommendation modes
- ✓ Generate sample recommendations

## ⚠️ Troubleshooting

### Issue: "No module named 'streamlit'"
**Solution**: `pip install streamlit`

### Issue: "No module named 'surprise'"
**Solution**: `pip install scikit-surprise`

### Issue: "Anime not found"
**Solution**: Check the exact anime name in the dataset. Names are case-sensitive.

### Issue: "User not found"
**Solution**: Ensure the user ID exists in the rating dataset. Check the Dataset Explorer for valid user IDs.

### Issue: Slow recommendations
**Reason**: First run trains the SVD model (can take a few minutes on large datasets)
**Solution**: Subsequent runs are faster due to caching. For very large datasets, reduce the SVD n_epochs parameter.

## 📈 Performance Optimization Tips

1. **Reduce SVD epochs**: Lower n_epochs in `model.py` for faster training
2. **Sample the data**: Use a subset of ratings for faster model training
3. **Cache results**: Streamlit automatically caches recommendation results
4. **Increase n_factors**: Can improve recommendation quality (but slower)

## 🎓 Key Algorithms

### TF-IDF (Content-Based)
```
1. Convert genres to TF-IDF vectors
2. Compute cosine similarity between anime
3. Return top N similar anime
```

### SVD (Collaborative)
```
1. Build utility matrix (users × anime)
2. Decompose using SVD (Matrix Factorization)
3. Predict missing ratings
4. Return anime with highest predicted ratings
```

### Hybrid
```
1. Get content-based scores
2. Get collaborative scores
3. Normalize both to 0-100
4. Combine with weights: score = w1*content + w2*collab
5. Return top N by hybrid score
```

## 📝 Code Quality

- ✅ Modular design (separate files for UI, models, utilities)
- ✅ Comprehensive error handling
- ✅ Detailed comments and docstrings
- ✅ Type hints and proper variable naming
- ✅ No hardcoded values
- ✅ Production-ready code

## 🔐 Data Privacy

- Local data processing only
- No data sent to external servers
- Datasets remain private to your machine

## 📚 References

- [Streamlit Documentation](https://docs.streamlit.io)
- [scikit-learn](https://scikit-learn.org)
- [Surprise Library](http://surpriselib.com)
- [TF-IDF Vectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)

## 🎯 Future Enhancements

- [ ] Deep learning embeddings (neural networks)
- [ ] Content-based filtering with more features
- [ ] User profile customization
- [ ] Recommendation explanations
- [ ] Real-time model updates
- [ ] Multiple recommendation algorithms
- [ ] User feedback integration
- [ ] Deployment to cloud (Heroku, AWS)

## 👨‍💻 Author

Machine Learning Engineering Team

## 📄 License

This project is provided as-is for educational purposes.

---

**Happy Anime Watching! 🍿🎬**
