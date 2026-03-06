#HUSSE Léna 21212867
#YÜKSEKKAYA Nehir 21307751

import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import random

#Q0.1 

def genereID2Name(fichier):
    dico = {}
    df = pd.read_csv(fichier)
    for l in range(len(df)):
        dico[str(df.iloc[l]['ID'])]=df.iloc[l]["Crop_french"]
    return dico

#Q1.1

def simulate_profit_legume(c,props,cost_model):
    aS=np.random.normal(cost_model["muAs"],cost_model["sigmaAs"])
    af=np.random.normal(cost_model["muAf"],cost_model["sigmaAf"])
    v=np.random.normal(cost_model["muV"],cost_model["sigmaV"])
    for i in range(len(props)):
        if(props.iloc[i]["Crop_french"]==c):
            ac=props.iloc[i]["ac"]
    z=aS+af+v+ac
    return (z, np.exp(z)) 

def distribution_rendement_legume(c,props, cost_model,N,bins):
    aS=np.random.normal(cost_model["muAs"],cost_model["sigmaAs"],N)
    af=np.random.normal(cost_model["muAf"],cost_model["sigmaAf"],N)
    v=np.random.normal(cost_model["muV"],cost_model["sigmaV"],N)
    for i in range(len(props)):
        if(props.iloc[i]["Crop_french"]==c):
            ac=props.iloc[i]["ac"]
    z= [aS[i]+af[i]+v[i]+ac for i in range(N)]
    y= [np.exp(i) for i in z]
    plt.hist(z,bins,density=False)
    plt.show()
    plt.hist(y,bins,density=False)
    plt.show()
    ez=np.mean(z)
    ey=np.mean(y)
    sz=np.std(z)
    sy=np.std(y)
    return(ez, sz,ey,sy)

def parametres_rendement_legume(c,props,cost_model):
    for i in range(len(props)):
        if(props.iloc[i]["Crop_french"]==c):
            ac=props.iloc[i]["ac"]
    ez= cost_model["muV"]+cost_model["muAf"]+cost_model["muAs"]+ac
    sz= ((cost_model["sigmaV"])**2+cost_model["sigmaAf"]**2+cost_model["sigmaAs"]**2)**0.5
    ey=np.exp(ez+sz**2/2)
    sy=((np.exp(sz**2)-1)*np.exp(2*ez+sz**2))**0.5
    return(ez,sz,ey,sy)


def simulate_charge_legume(c,props,cost_model):
    aS=np.random.normal(cost_model["muBs"],cost_model["sigmaBs"])
    af=np.random.normal(cost_model["muBf"],cost_model["sigmaBf"])
    v=np.random.normal(cost_model["muW"],cost_model["sigmaW"])
    for i in range(len(props)):
        if(props.iloc[i]["Crop_french"]==c):
            ac=props.iloc[i]["bc"]
    z=aS+af+v+ac
    return (z, np.exp(z)) 

#Q2

