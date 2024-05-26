import sys
import pickle
import uvicorn
import pandas as pd
from fastapi import FastAPI

# Inicia API
app = FastAPI()

# Carrega modelo
sys.path.append('src')
with open('models/recommender.pkl', 'rb') as file:
    recommender = pickle.load(file)

# Cria página inicial
@app.get('/')
def home():
    return 'Welcome to the Steam Game Recommender app!'

# Lista jogos
@app.get('/list_games')
def list_games():
    return recommender.scores_.index.tolist()

# Procura jogos por substring
@app.get('/search_games')
def search_games(pattern):
    pattern = pattern.lower()
    games = pd.Series(recommender.scores_.index.tolist())
    games_matched = games[games.str.lower().str.contains(pattern)]
    return games_matched

# Recomenda jogo
@app.get('/recommend')
def recommend(game: str, max_recommendations: int = 10):
    return recommender.recommend(game, max_recommendations)

# Executa API
if __name__ == '__main__':
    uvicorn.run(app)

