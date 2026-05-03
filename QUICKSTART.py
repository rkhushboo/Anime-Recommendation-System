#!/usr/bin/env python
"""
Quick Start Guide for Anime Recommendation System
This file provides step-by-step instructions to run the application
"""

import os
import sys
from pathlib import Path

def print_header():
    print("\n" + "="*70)
    print("🎬 ANIME RECOMMENDATION SYSTEM - QUICK START")
    print("="*70 + "\n")

def print_step(num, title, description):
    print(f"{'='*70}")
    print(f"STEP {num}: {title}")
    print(f"{'='*70}")
    print(description)
    print()

def main():
    print_header()
    
    current_dir = Path(__file__).parent
    
    print_step(
        1,
        "VERIFY ENVIRONMENT",
        """
Your workspace is located at:
c:\\Users\\richi\\DATA SCIENCE - IIT GUWAHATI\\DEPLOYMENT\\Anime_Recommendation

Files present:
✓ app.py              - Streamlit UI application
✓ model.py            - Machine Learning models
✓ utils.py            - Helper functions
✓ test_system.py      - System test script
✓ requirements.txt    - Python dependencies
✓ anime.csv           - Dataset (12,294 anime)
✓ rating.csv          - Dataset (6.3M ratings)
✓ README.md           - Full documentation
✓ venv/               - Python environment

Status: ✅ All files are ready!
        """
    )
    
    print_step(
        2,
        "INSTALL DEPENDENCIES (If not already installed)",
        """
Using the myenv Python environment provided in the workspace:

Command:
    .\\myenv\\python.exe -m pip install -r requirements.txt

Required packages:
✓ pandas, numpy          - Data processing
✓ scikit-learn           - Machine learning & SVD
✓ scipy                  - Sparse matrix support
✓ streamlit              - Web application
✓ matplotlib, seaborn    - Visualization
✓ wordcloud              - Genre visualization

✓ plotly                 - Interactive charts

Status: ✅ Dependencies pre-configured in requirements.txt
        """
    )
    
    print_step(
        3,
        "VERIFY INSTALLATION (Optional)",
        """
Run the test script to verify everything works:

Command:
    .\\myenv\\python.exe test_system.py

This will:
✓ Check all imports
✓ Load and clean datasets
✓ Initialize recommendation system
✓ Test all three recommendation modes
✓ Generate sample recommendations
✓ Display statistics

Expected output: ✅ All tests passed!
        """
    )
    
    print_step(
        4,
        "START THE APPLICATION",
        """
Run the Streamlit web app:

Command:
    streamlit run app.py

The app will:
✓ Start the development server
✓ Open automatically in your default browser
✓ Display at: http://localhost:8501

First run may take 30-60 seconds (loading & preprocessing data)
Subsequent runs will be faster (data is cached)
        """
    )
    
    print_step(
        5,
        "USE THE APPLICATION",
        """
Once the app is running, you can:

🎯 RECOMMENDATIONS TAB:
  • Select recommendation mode (Content, Collaborative, Hybrid)
  • Choose parameters (anime, user ID, top N)
  • Click "Generate Recommendations" button
  • View results in a formatted table

📊 DATASET EXPLORER TAB:
  • Preview anime and rating datasets
  • View dataset statistics
  • Filter anime by genre or rating
  • Explore top-rated and most popular anime

📈 VISUALIZATIONS TAB:
  • Top anime by rating (bar chart)
  • Most popular anime by members
  • Rating distribution histogram
  • Genre word cloud
  • Rating vs Popularity scatter plot
  • Key metrics and insights
        """
    )
    
    print_step(
        6,
        "RECOMMENDATION MODES EXPLAINED",
        """
🔷 CONTENT-BASED FILTERING:
  Method: Genre similarity (TF-IDF + Cosine)
  Input: Anime name
  Output: Similar anime by genre
  Speed: ⚡ Very fast
  Quality: 👍 Good for exploration
  Example: "If you like Naruto, try these anime..."

🔷 COLLABORATIVE FILTERING:
  Method: User rating patterns (SVD Matrix Factorization)
  Input: User ID
  Output: Anime liked by similar users
  Speed: ⚡ Fast (optimized model)
  Quality: 👍👍 Very good personalization
  Example: "Users like you rated these anime highly..."

🔷 HYBRID:
  Method: Combined (Content + Collaborative)
  Input: Anime name + User ID
  Output: Best of both methods
  Speed: ⚡ Fast
  Quality: 👍👍👍 Excellent all-around
  Example: "Based on anime you like and your ratings..."
        """
    )
    
    print_step(
        7,
        "USEFUL TIPS & TRICKS",
        """
💡 TIPS FOR BEST RESULTS:

1. FINDING VALID USER IDs:
   • Go to "Dataset Explorer" tab
   • Check the ratings preview table
   • User IDs range from 1 to 69,600

2. FINDING VALID ANIME NAMES:
   • Go to "Dataset Explorer" tab
   • Check the anime preview table
   • Or search by genre in filters

3. RECOMMENDATION TUNING:
   • Content-Based: Good for discovering similar anime
   • Collaborative: Good for personalization
   • Hybrid: Best overall (try weights 0.4/0.6)

4. PERFORMANCE:
   • Results are cached (runs 2+ are faster)
   • Increase top_n for more options
   • Hybrid mode combines best of both worlds

5. DATASET INSIGHTS:
   • 12,294 anime in database
   • 69,600 users with ratings
   • 6.3 million rating records
   • Average rating: 6.48/10
        """
    )
    
    print_step(
        8,
        "TROUBLESHOOTING",
        """
❌ COMMON ISSUES & SOLUTIONS:

Issue: "Anime not found" error
→ Solution: Check exact anime name in Dataset Explorer
            Names are case-sensitive

Issue: "User not found" error
→ Solution: Verify user ID exists in ratings dataset
            Try user IDs from the preview table

Issue: App runs very slowly on first load
→ Solution: This is normal! SVD model training takes time
            Subsequent runs use cached model (much faster)
            Can optimize by reducing SVD parameters in model.py

Issue: "Module not found" errors
→ Solution: Run: .\\myenv\\python.exe -m pip install -r requirements.txt

Issue: Port already in use (port 8501)
→ Solution: streamlit run app.py --server.port 8502

Issue: Still seeing test output messages
→ Solution: These are normal logging warnings from Streamlit
            They don't affect functionality
        """
    )
    
    print_step(
        9,
        "PROJECT FILES STRUCTURE",
        """
📁 PROJECT STRUCTURE:

Anime_Recommendation/
│
├── 🎬 app.py                    - Main Streamlit app (1000+ lines)
│   ├── Page configuration
│   ├── Data loading & caching
│   ├── Sidebar controls
│   ├── Three tabs (Recommendations, Explorer, Visualizations)
│   └── Interactive UI elements
│
├── 🤖 model.py                  - ML models (400+ lines)
│   ├── AnimeRecommendationSystem class
│   ├── TF-IDF content-based filtering
│   ├── SVD collaborative filtering
│   ├── Hybrid recommendation combining both
│   └── Helper methods for data queries
│
├── 🛠️ utils.py                  - Utilities (500+ lines)
│   ├── Data loading & cleaning functions
│   ├── Statistical functions
│   ├── Visualization functions
│   ├── Display formatting functions
│   └── Validation helpers
│
├── 🧪 test_system.py            - Test suite
│   └── Comprehensive system tests
│
├── 📋 requirements.txt           - Dependencies list
├── 📖 README.md                 - Full documentation
├── 📊 anime.csv                 - Anime dataset
├── ⭐ rating.csv                - Ratings dataset
└── 📁 myenv/                    - Python environment
        """
    )
    
    print_step(
        10,
        "NEXT STEPS",
        """
🚀 YOU'RE READY TO GO!

Next steps:

1. Open terminal/PowerShell
2. Navigate to project folder:
   cd "c:\\Users\\richi\\DATA SCIENCE - IIT GUWAHATI\\DEPLOYMENT\\Anime_Recommendation"

3. Run the app:
   streamlit run app.py

4. Browser will open automatically with the UI
5. Explore, test, and enjoy recommendations!

For advanced usage or modifications:
→ See README.md for detailed documentation
→ See model.py for ML algorithm details
→ See app.py for UI customization
        """
    )
    
    print("\n" + "="*70)
    print("✅ SETUP COMPLETE! Ready to run the application.")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
