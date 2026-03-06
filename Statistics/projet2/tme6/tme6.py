#Lena Husse 21212867
#Nehir Yüksekkaya 21307751

import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import random

months=np.array(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

def filtre_database(csv, marketing, climat):
    df = pd.read_csv(csv)
    res = (df['Marketing'] == marketing) & (df['Climate'] == climat)
    return df.iloc[[i for i, f in enumerate(res) if f]]

def add_sales_duration(cycles):
    res = pd.DataFrame()
    res=cycles[["Sale_"+i for i in months]]
    tot=[]
    for i in range(len(res)):
        tot.append(np.sum(res.iloc[i]))
    new=cycles.assign(Sales_duration= tot)
    return new

def choose_cycle(cycles,demands,category,month):
    res=[]
    for i in range (len(demands)):
        if (demands.iloc[i]['Crop category']==category and demands.iloc[i]["Minimal number of crops_"+month]>0):
            for j in range (len(cycles)):
                if(cycles.iloc[j]['Crop category']==category and cycles.iloc[j]["Sale_"+month]==1):
                    res.append(j)
    if res == []:
        return False
    return (cycles.iloc[random.choice(res)])['ID']

def update_production(productions,id_cycle,cycles):
    if id_cycle not in cycles['ID']:
        return False
    index = (cycles[cycles['ID']==id_cycle].index)[0]
    if id_cycle not in productions:
        productions[id_cycle]=cycles.loc[index]['Shmin_month']*cycles.loc[index]['Harvest_total']
    else:
        if productions[id_cycle] < cycles.loc[index]['Shmax_total']:
            productions[id_cycle]+=1
        else:
            return False
    return True

    """Crop category,Climate,Marketing,
    Minimal quantity of shares_Jan,
    Minimal quantity of shares_Feb,Minimal quantity of shares_Mar,
    Minimal quantity of shares_Apr,Minimal quantity of shares_May,
    Minimal quantity of shares_Jun,Minimal quantity of shares_Jul,
    Minimal quantity of shares_Aug,Minimal quantity of shares_Sep,
    Minimal quantity of shares_Oct,Minimal quantity of shares_Nov,
    Minimal quantity of shares_Dec,Minimal number of crops_Jan,
    Minimal number of crops_Feb,Mar,
    Minimal number of crops_Apr,Minimal number of crops_May,
    Minimal number of crops_Jun,Minimal number of crops_Jul,
    Minimal number of crops_Aug,Minimal number of crops_Sep,
    Minimal number of crops_Oct,Minimal number of crops_Nov,
    Minimal number of crops_Dec,
    Minimal number of crops per trimester_T1,
    Minimal number of crops per trimester_T2,
    Minimal number of crops per trimester_T3,
    Minimal number of crops per trimester_T4"""

    