import numpy as np
#Nehir YUKSEKKAYA 21307751
#Lena HUSSE 21212867
class Bandit:
    def __init__(self, n):
        self.nb_machinesous = n
        self.bandits = np.random.rand(n)

    #donne 1 s'il a gagne a la machine i, 0 sinon
    def play(self, i):
        tir = np.random.rand()
        if (tir < self.bandits[i]):
            return 1
        else:
            return 0    
        

class AgentBanditRandom:
    def __init__(self, n):
        self.nb_machinesous = n
        self.times = np.zeros(n)
        self.rewards = np.zeros(n)

    #reourne le num de la machine sur laquelle il joue
    def play(self):
        return np.random.randint(0, self.nb_machinesous)

    #prend i le num de la machine et r la recompense gagnee sur i
    def reward(self, i, r):
        self.times[i] += 1
        self.rewards[i] += r

    def reset(self):
        self.times = np.zeros(self.nb_machinesous)
        self.rewards = np.zeros(self.nb_machinesous)


class JeuBandit:
    def __init__(self, bandit, agent):
        self.bandit = bandit
        self.agent = agent
        self.rewards = np.zeros(self.agent.nb_machinesous)

    def reset(self):
        self.agent.reset()
        self.rewards = np.zeros(self.agent.nb_machinesous)

    #un agent joue n fois
    def play(self, n):
        self.reset()
        for i in range(n):
            machine = self.agent.play()
            rec = self.bandit.play(machine)
            self.agent.reward(machine, rec)
            self.rewards[machine]+=rec


class AgentGlouton(AgentBanditRandom): 
    # machine est la machine la plus rentable
    def __init__(self, n, n_explo=20):
        super().__init__(n)
        self.n_explo = n_explo


    #reourne le num de la machine sur laquelle il joue (la plus efficace)
    def play(self):
        # cpt = 0
        # jeu = JeuBandit(Bandit(self.nb_machinesous), AgentBanditRandom(self.nb_machinesous))
        if np.sum(self.times) < self.n_explo:
            return int(np.sum(self.times) % self.nb_machinesous)
        # print(np.argmax(self.rewards))
        return np.argmax(self.rewards)
        
    def reward(self, i, r):
        super().reward(i, r)

    def reset(self):
        super().reset()

