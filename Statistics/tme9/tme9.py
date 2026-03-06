#HUSSE Léna 21212867
#YÜKSEKKAYA Nehir 21307751


import utils
import numpy as np
import pandas as pd

def nbParams(data,att=None):
    if(att==None):
        att=data.columns
    nb_att = len(att)
    nb_var=1
    for i in range (nb_att):
        attri = att[i]
        nb_var *= np.unique(data[attri]).size
    print((str)(nb_att) + " varibales : " + (str)(nb_var*8) + " octets")
    return nb_var*8

def nbParamsIndep(data):
    att = data.columns
    nb_var=0
    nb_att = len(att)
    for i in range (len(att)):
        nb_var += np.unique(data[att[i]]).size
    print((str)(nb_att) + " varibales : " + (str)(nb_var*8) + " octets")
    return nb_var*8

#####
# Question 3.3a
#####
# P(A,B,C)=P(A,C|B)*P(B)
#         = P(A|B)*P(C|B)*P(B)
#         = p(A,B)*P(C|B)
#         = P(B|A)*P(A)*P(C|B)
#####


def draw_5_variables_independantes():
    return utils.drawGraph("A B C D E F")

def draw_5_variables_sans_independances():
    return utils.drawGraph("A->B->C->D->E->F")

def drawNaiveBayes(train,target):
    s=""
    for i in train.columns:
        if i!=target:
            s+=target+"->"+i+";"
    return utils.drawGraph(s)

def nbParamsNaiveBayes(data,target,att=None):
    if(att==None):
        att=data.columns
    nb_att = len(att)
    nb_target=np.unique(data[target]).size
    nb_var = nb_target
    for i in range (nb_att):
        attri = att[i]
        if(attri!=target):
            nb_var += np.unique(data[attri]).size*nb_target
    print((str)(nb_att) + " varibales : " + (str)(nb_var*8) + " octets")
    return nb_var*8
