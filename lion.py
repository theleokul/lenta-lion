from typing import List
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta as rdelta

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import operator

data_dirpath = 'data'
transactions_filepath = Path(data_dirpath, 'trans_mat_corr.csv')
transaction_df = pd.read_csv(transactions_filepath)
transaction_df['chq_date_e'] = pd.to_datetime(transaction_df['chq_date'], format='%Y-%m-%d')
month_history = pd.read_csv(Path(data_dirpath, 'month_history.csv'))
materials = pd.read_csv(Path(data_dirpath, 'materials.csv'))


def _get_cosine_similar_products(material, date, plant, month_history=month_history, 
                                 materials=materials[['material', 'hier_level_1', 'is_private_label', 'is_alco']]):
    scaler = StandardScaler()
    materials_set = set(materials.material.values)
    if not material in materials_set:
        return 'Oops! Unknown item. Add item to database'
    
    col_name = month_history.set_index(['material', 'month']).unstack().reset_index().columns
    col_name_list = ['material']
    for ind in col_name[1:]:
        col_name_list.append(ind[0] + ' ' + ind[1])

    vecs_for_materials = pd.DataFrame(month_history.set_index(['material', 'month']).unstack().reset_index().values, columns=col_name_list)
    vecs_for_materials = pd.merge(vecs_for_materials, materials[['material', 'hier_level_1', 'is_private_label', 'is_alco']], on='material', how='outer')
    
    target_material = vecs_for_materials[vecs_for_materials.material == material].fillna(0) ## по возможности исправить fillna
    other_materials = vecs_for_materials[vecs_for_materials.material != material].fillna(0) ## по возможности иправить
    
    scaler.fit(vecs_for_materials.values[:, 1:])
    scaled_target_vec = scaler.transform(target_material.values[:, 1:])
    scaled_other = scaler.transform(other_materials.values[:, 1:])
    
    cos_sim_arr = cosine_similarity(scaled_target_vec, scaled_other)
    other_materials['cossim'] = cos_sim_arr[0]
    
    out_material_arr = other_materials[other_materials.cossim == cos_sim_arr.max()].material.values    
    return out_material_arr


def _check_availability(prods: List[str], plant_id: str, order_date: str):
    # TODO: Implement check of availabitiy
    availabitiy = [True for _ in prods]

    # HACK: Due to lack of actual implementation of this function
    # this hack allows to also use this function in correlation_gear
    if len(availabitiy) > 1:
        availabitiy[-1] = False  # Test 
    return availabitiy


def _similarity_gear(card_id: str, fav_prods: List[str], plant_id: str, order_date: str):
    """
        Make sure that fav_prods is available in plant_id at order_date.
        If goods are available when return themselve,
        otherwise find available similar products and calculate discounts.
    """

    availability = _check_availability(prods=fav_prods, plant_id=plant_id, order_date=order_date)
    
    unavailability = list(map( operator.not_, availability))
    chng_prods = np.array(fav_prods)[unavailability]
    stable_prods = list(np.array(fav_prods)[availability])
    
    
    new_prods = []
    for prod in chng_prods:
        new_prod = _get_cosine_similar_products(prod, order_date, plant_id)[0]
        new_prods.append(new_prod)
    
    return_prods = stable_prods + new_prods
    return_dict = dict(zip(return_prods, np.concatenate([np.zeros(len(stable_prods)), np.ones(len(new_prods))])))
    
    return return_prods, return_dict


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

    # HACK: Avoid difference in transaction_df and materials.
    # Better to make them consistent and use random.
    # fav_prods_sample = np.random.choice(fav_prods, size=2, replace=False)
    fav_prods_sample = fav_prods[:2]

    add_prods = []
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
    return recommended_prods, discounts


## DEBUG
# goods_array, discounts = roar_basket(
#     'c23395'
#     ,['m61505', 'm55357', 'm22242']
#     ,'pl293' 
#     ,'2017-06-20'
# )

# print(goods_array, discounts)
##
