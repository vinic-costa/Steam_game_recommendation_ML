import pickle
import numpy as np
from utils import get_steam_data, get_ratings, ItemBasedRecommender

# Get data
df = get_steam_data('data/steam-200k.csv')
# Get implicit ratings
df_ratings = get_ratings(df)

# Instiantiate recommender
recommender = ItemBasedRecommender(
    data=df_ratings,
    item_col='item_id',
    user_col='user_id',
    score_col='rating',
    aggfunc=np.sum
)

# Train recommender
recommender.fit()

# Save recommender
with open('models/recommender.pkl', 'wb') as model_file:
    pickle.dump(recommender, model_file)
