#Léna HUSSE 21212867
#Nehir YÜKSEKKAYA 21307751

import utils as u
import numpy as np


# liste des classes et fonctions de ce fichier :
#  - getNthDict (remplit un dictionnaire avec la ligne n d'un dataframe)
#  - viewData (visualisation d'un dataframe)
#  - discretizeData (discrétisation automatique)
#  - AbstractClassifier (classe abstraite pour tous les classifieurs)
#  - drawGraphHorizontal (dessin d'un graphe orienté horizontal)
#  - drawGraph (dessin d'un graphe orienté vertical)

def getPrior(data):
    dic = {}
    dic["estimation"] = np.sum(data["target"]) / len(data)
    dic["min5pourcent"] = dic["estimation"]*0.95
    dic["max5pourcent"] = dic["estimation"] * 1.05
    return dic

class APrioriClassifier(u.AbstractClassifier):
    def __init__(self,donnes):
        self.data = donnes

    def estimClass(self, dico):
        dico = getPrior(self.data)
        if (dico["estimation"])>=0.5 : 
            return 1
        else : 
            return 0

    def statsOnDF(self, data):
        classe = self.estimClass(getPrior(data))
        VP = 0 
        VN = 0 
        FP = 0 
        FN = 0
        for t in data.itertuples():
            dic=t._asdict()
            target=dic['target']
            if(target == 1 and classe == 1) :
                VP += 1
            if(target == 1 and classe == 0) :
                FN += 1
            if(target == 0 and classe == 1) :
                FP += 1
            if(target == 0 and classe == 0) :
                VN += 1
        pre = VP / (VP + FP)
        rap = VP / (VP + FN)
        return {'VP' : VP, 'VN':VN,'FP':FP,'Fn':FN,'Précision':pre,'Rappel':rap}

def P2D_l(df,attr):
    dico = {1:{},0:{}}
    target1 = df['target']==1
    list1=[]
    list0=[]
    for i in range (len(target1)):
        if(target1[i]==True):
            list1.append(i)
        else:
            list0.append(i)
    dico1={}
    dico0={}
    tot1 = 0
    tot0=0
    for i in range(len(df)):
        if i in list1:
            tot1 += 1
            if df.iloc[i][attr] not in dico1:
                dico1[df.iloc[i][attr]] = 1
            if df.iloc[i][attr] in dico1:
                dico1[df.iloc[i][attr]] += 1
        if i in list0:
            tot0+=1
            if df.iloc[i][attr] not in dico0:
                dico0[df.iloc[i][attr]] = 1
            if df.iloc[i][attr] in dico0:
                dico0[df.iloc[i][attr]] += 1

    for elem in dico1:
        dico1[elem]=(dico1[elem]/tot1)
    
    for elem in dico0:
        dico0[elem]=(dico0[elem]/tot0)
    dico[1] = dico1
    dico[0] = dico0
    return dico

def P2D_p(df,attr):
    dico={int:{int:float}}
    lista=np.unique(df[attr])
    for i in lista:
        for data in df.itertuples():
            dic=data._asdict()
            tar=dic['target']
            at=dic[attr]
            if at==i:
                if tar==1:
                    dico[i][1]+=1


    
    
