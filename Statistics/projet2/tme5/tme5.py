#Lena Husse 21212867
#Nehir Yüksekkaya 21307751

import numpy as np
from matplotlib import pyplot as plt


def get_valid_indices_all_vars(data,colonnes):
    liste_ind = []
    liste_non = []
    cpt = 0
    for nom_col in colonnes:
        c = data[nom_col]
        for l in c:
            if(cpt not in liste_ind):
                liste_ind.append(cpt)
            if (not l>0):
                liste_non.append(cpt)
            cpt+=1
        cpt = 0
    return [i for i in liste_ind if i not in liste_non]


def compute_LER(data):
    ler1 = np.array(data['Crop_1_yield_intercropped'] / data['Crop_1_yield_sole'])
    ler2 = np.array(data['Crop_2_yield_intercropped'] / data['Crop_2_yield_sole'])
    return np.array(ler1+ler2)

def plot_compare_LERs(colonne, LER):
    _, ax = plt.subplots(1, 3, figsize=(15,5))
    ax[0].scatter(colonne,LER, s=5,color="green")
    l=sorted(colonne-LER)
    ax[1].scatter( range(len(LER)),l, s=5, color="purple")
    ax[2].hist(l, 30, color="skyblue", edgecolor="black")
    plt.show()