import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Get data
def get_steam_data(file_path:str) -> pd.DataFrame:
  column_names = ['user_id', 'item_id', 'behaviour', 'hours']
  df = pd.read_csv(file_path, header=None, names=column_names, usecols=range(4))
  return df

# Função para capturar avaliações implícitas
def get_ratings(df: pd.DataFrame) -> pd.DataFrame:
  """Get implicit ratings per game"""
  df_user_consumption = (
      df
      .query('behaviour == "play"')[['user_id', 'item_id', 'hours']]
      .groupby(['user_id'])['hours']
      .sum()
      .reset_index()
      .rename({'hours': 'total_user_hours'}, axis=1)
  )

  df_ratings = (
    df
    .query('behaviour == "play"')[['user_id', 'item_id', 'hours']]
    .groupby(['user_id', 'item_id'])['hours']
    .sum()
    .reset_index()
    .merge(df_user_consumption, on='user_id')
  )

  df_ratings['rating'] = df_ratings['hours']/df_ratings['total_user_hours']
  df_ratings.drop(columns=['hours', 'total_user_hours'], inplace=True)

  return df_ratings


# Classe genérica para recomendação
class ItemBasedRecommender:
  
  def __init__(self, data, item_col, user_col, score_col, aggfunc=np.mean):
    self.data = data.copy()
    self.item_col = item_col
    self.user_col = user_col
    self.score_col = score_col
    self.aggfunc = aggfunc
 
  def fit(self, sample_size=None, normalize=False, n_most_popular=10):
    
    if sample_size is not None:
      self.item_sample_ = self.data.groupby(self.item_col)[self.user_col] \
        .nunique() \
        .sort_values(ascending=False) \
        .to_frame('nunique_customers') \
        .head(sample_size) \
        .index.tolist()
      self.data = self.data[self.data[self.item_col].isin(self.item_sample_)]

    self.scores_ = self.data.groupby(self.item_col).agg(**{
        f'{self.score_col}_{self.aggfunc.__name__}': (self.score_col, self.aggfunc),
        f'{self.score_col}_count': ('rating', 'count')
        }).sort_values(f'{self.score_col}_count', ascending=False)

    self.n_most_popular_ = self.data[self.item_col].value_counts().nlargest(n_most_popular).index

    self.data_pivot_ = self.data.pivot(index=self.item_col, columns=self.user_col, values=self.score_col)
    if normalize:
      avg_ratings = self.data_pivot_.mean(axis=0)
      self.data_pivot_ = self.data_pivot_.sub(avg_ratings, axis=1).fillna(0)
    else:
      self.data_pivot_ = self.data_pivot_.fillna(0)

    self.sim_matrix_ = cosine_similarity(self.data_pivot_)
    self.sim_matrix_ = pd.DataFrame(self.sim_matrix_, index=self.data_pivot_.index, columns=self.data_pivot_.index)
    return self
    
  def recommend(self, target_item, max_recommendations=None):
    try:
      return self.sim_matrix_.loc[target_item].drop(target_item).sort_values(ascending=False).head(max_recommendations)
    except KeyError as e:
      print(f'\033[1m{target_item}\033[0;0m is not included in the recommendation matrix. Returning top 10 items:\n')
      return self.n_most_popular_

  def fit_recommend(self, target_item):
    return self.fit().recommend(target_item)
