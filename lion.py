from typing import List
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta as rdelta

import numpy as np
import pandas as pd

data_dirpath = 'data'
transactions_filepath = Path(data_dirpath, 'trans_mat_corr.csv')
transaction_df = pd.read_csv(transactions_filepath)
# materials_filepath = Path(data_dirpath, 'materials_encoded.csv')
# materials_df = pd.read_csv(materials_filepath)
# materials_df = materials_df.drop('Unnamed: 0', axis=1)
# transaction_df = transaction_df.merge(materials_df, on='material')
transaction_df['chq_date_e'] = pd.to_datetime(transaction_df['chq_date'], format='%Y-%m-%d')
# transaction_df = transaction_df.sort_values(['chq_date_e', 'material'])

# order_date = datetime.strptime('2017-06-20', '%Y-%m-%d')
# bottom_date = order_date - rdelta(months=1)
# prev_month_transaction_df = transaction_df[
#     (transaction_df.chq_date_e >= bottom_date)
#     & (transaction_df.chq_date_e <= order_date)
# ]

# prev_month_transaction_df.to_csv('data/trans_mat_corr.csv', index=False)

# print(transaction_df.client_id.value_counts()[:30])

def _check_availability(prods: List[str], plant_id: str, order_date: str):
    # TODO: Implement check of availabitiy
    availabitiy = [True for _ in prods]
    # availabitiy[-1] = False  # Test 
    return availabitiy


def _similarity_gear(card_id: str, fav_prods: List[str], plant_id: str, order_date: str):
    """
        Make sure that fav_prods is available in plant_id at order_date.
        If goods are available when return themselve,
        otherwise find available similar products and calculate discounts.
    """

    # TODO: Implement similarity_gear
    return fav_prods, {p: 0 for p in fav_prods}


def _correlation_gear(fav_prods: List[str], plant_id: str, order_date: str):
    """
        Find goods that are usually taken with fav_prods.
        It is supposed that fav_prods were gone through the similarity_gear.
    """

    order_date = datetime.strptime(order_date, '%Y-%m-%d')
    bottom_date = order_date - rdelta(months=1)

    prev_month_transaction_df = transaction_df[
        (transaction_df.chq_date_e >= bottom_date)
        & (transaction_df.chq_date_e <= order_date)
    ]
    cl_mat_counts_df = pd.pivot_table(
        prev_month_transaction_df 
        ,index='client_id'
        ,columns='material' 
        ,values='chq_date_e' 
        ,aggfunc='count'
    )

    # HACK: We can work only with goods that are represented well 
    # (more than 30 clients bought them)
    cl_mat_counts_df = cl_mat_counts_df.loc[:, (cl_mat_counts_df.count(axis=0) >= 30)]

    fav_prods_sample = np.random.choice(fav_prods, size=2, replace=False)

    add_prods = []
    print('Hello world corr')
    for p in fav_prods_sample:
        prod_to_complement = cl_mat_counts_df[p]
        similar_prods = cl_mat_counts_df.corrwith(prod_to_complement)
        similar_prods = similar_prods.dropna()
        similar_prods = pd.DataFrame(similar_prods)
        similar_prods = similar_prods.sort_values(0, ascending=False)
        similar_prods = similar_prods[~similar_prods.index.isin(fav_prods_sample)]

        for sim_p, corr in similar_prods.iterrows():
            if all(_check_availability([sim_p], plant_id, order_date)):
                add_prods.append(sim_p)
                break

    return fav_prods + add_prods


def roar_basket(card_id: str, fav_prods: List[str], plant_id: str, order_date: str):
    """
        Receive as an input features collected from the lion's interface (e.x. telegram-bot):
        -- card_id
        -- fav_prods - three favourite products
        -- plant_id
        -- order_time - desired time in which client want to get his basket
    """

    fav_prods, discounts = _similarity_gear(card_id, fav_prods, plant_id, order_date)
    recommended_prods = _correlation_gear(fav_prods, plant_id, order_date)
    print('Hello world roar')
    return recommended_prods, discounts


# goods_array, discounts = roar_basket(
#     'c23395'
#     ,['m61505', 'm55357', 'm22242']
#     ,'pl293' 
#     ,'2017-06-20'
# )

# print(goods_array, discounts)