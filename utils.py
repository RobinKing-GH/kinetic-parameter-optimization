from scipy.special import comb
from itertools import combinations
import numpy as np
import copy
import math
import win32com.client 

""" ************************************      1, The population is partitioned into non-dominated fronts    ************************************ """
def NDsort(mixpop,N,M):
    # mixpop：Function values corresponding to the parent and offspring populations to be sorted；
    # N：Number of uniformly distributed points generated；
    # M：Number of optimization objectives；
    nsort = N
    N,M = mixpop.shape[0],mixpop.shape[1]
    Loc1 = np.lexsort(mixpop[:,::-1].T)
    mixpop2 = mixpop[Loc1]
    Loc2 = Loc1.argsort()
    frontno = np.ones(N)*(np.inf)
    maxfno = 0
    while (np.sum(frontno < np.inf) < min(nsort,N)):
        maxfno = maxfno+1
        for i in range(N):
            if (frontno[i] == np.inf):
                dominated = 0
                for j in range(i):
                    if (frontno[j] == maxfno):
                        m=0
                        flag=0
                        while (m<M and mixpop2[i,m]>=mixpop2[j,m]):
                            if(mixpop2[i,m]==mixpop2[j,m]):
                                flag=flag+1
                            m=m+1 
                        if (m>=M and flag < M):
                            dominated = 1
                            break
                if dominated == 0:
                    frontno[i] = maxfno
    frontno=frontno[Loc2]
    return frontno,maxfno


""" ************************************        2、 Determination of Reference Points on a Hyperplane        ************************************ """
def uniformpoint(N,M):
    # Generation of Uniform Reference Points as a Function of Population Size and Objective Count
    H1=1
    while (comb(H1+M-1,M-1)<=N):
        H1=H1+1
    H1=H1-1
    W=np.array(list(combinations(range(H1+M-1),M-1)))-np.tile(np.array(list(range(M-1))),(int(comb(H1+M-1,M-1)),1))
    W=(np.hstack((W,H1+np.zeros((W.shape[0],1))))-np.hstack((np.zeros((W.shape[0],1)),W)))/H1
    if H1<M:
        H2=0
        while(comb(H1+M-1,M-1)+comb(H2+M-1,M-1) <= N):
            H2=H2+1
        H2=H2-1
        if H2>0:
            W2=np.array(list(combinations(range(H2+M-1),M-1)))-np.tile(np.array(list(range(M-1))),(int(comb(H2+M-1,M-1)),1))
            W2=(np.hstack((W2,H2+np.zeros((W2.shape[0],1))))-np.hstack((np.zeros((W2.shape[0],1)),W2)))/H2
            W2=W2/2+1/(2*M)
            W=np.vstack((W,W2))
    W[W<1e-6]=1e-6
    N=W.shape[0]
    return W,N


""" ************************************                 3、 Source Code: Selection Module                  ************************************ """

def pdist(x,y):
    # Compute the cosine similarity between two vector matrices;
    x0=x.shape[0]
    y0=y.shape[0]
    xmy=np.dot(x,y.T)
    xm=np.array(np.sqrt(np.sum(x**2,1))).reshape(x0,1)
    ym=np.array(np.sqrt(np.sum(y**2,1))).reshape(1,y0)
    xmmym=np.dot(xm,ym)
    cos = xmy/xmmym
    return cos

def lastselection(popfun1,popfun2,K,Z,Zmin):
    popfun = copy.deepcopy(np.vstack((popfun1, popfun2)))-\
    np.tile(Zmin,(popfun1.shape[0]+popfun2.shape[0],1))
    N,M = popfun.shape[0],popfun.shape[1]
    N1 = popfun1.shape[0]
    N2 = popfun2.shape[0]
    NZ = Z.shape[0]
    extreme = np.zeros(M)
    w = np.zeros((M,M))+1e-6+np.eye(M)
    for i in range(M):
        extreme[i] = np.argmin(np.max(popfun/(np.tile(w[i,:],(N,1))),1))
    extreme = extreme.astype(int)
    temp = np.linalg.pinv(np.mat(popfun[extreme,:]))
    hyprtplane = np.array(np.dot(temp,np.ones((M,1))))
    a = 1/hyprtplane
    if np.sum(a==math.nan) != 0:
        a = np.max(popfun,0)
    np.array(a).reshape(M,1)
    a=a.T
    popfun = popfun/(np.tile(a,(N,1)))
    cos = pdist(popfun,Z)
    distance = np.tile(np.array(np.sqrt(np.sum(popfun**2,1))).reshape(N,1),(1,NZ))*np.sqrt(1-cos**2)
    d = np.min(distance.T,0)
    pi = np.argmin(distance.T,0)
    rho = np.zeros(NZ)
    for i in range(NZ):
        rho[i] = np.sum(pi[:N1] == i)
    choose = np.zeros(N2)
    choose = choose.astype(bool)
    zchoose = np.ones(NZ)
    zchoose = zchoose.astype(bool)
    while np.sum(choose) < K:
        temp = np.ravel(np.array(np.where(zchoose == True)))
        jmin = np.ravel(np.array(np.where(rho[temp] == np.min(rho[temp]))))
        j = temp[jmin[np.random.randint(jmin.shape[0])]]
        I = np.ravel(np.array(np.where(pi[N1:] == j)))
        I = I[choose[I] == False]
        if (I.shape[0] != 0):
            if (rho[j] == 0):
                s = np.argmin(d[N1+I])
            else:
                s = np.random.randint(I.shape[0])
            choose[I[s]] = True
            rho[j] = rho[j]+1
        else:
            zchoose[j] = False
    return choose

def envselect(mixpop,N,Z,Zmin,M,D):
    mixpopfun = cal(mixpop)
    frontno,maxfno = NDsort(mixpopfun,N,M)
    Next = frontno < maxfno
    Last = np.ravel(np.array(np.where(frontno == maxfno)))
    choose = lastselection(mixpopfun[Next,:],mixpopfun[Last,:],N-np.sum(Next),Z,Zmin)
    Next[Last[choose]] = True
    pop = copy.deepcopy(mixpop[Next,:])
    return pop


""" ************************************                       4、 Genetic Operator                         ************************************ """
def GO(pop,t1,t2,pc,pm,pre_exp):  # Genetic Operation
    pop1 = copy.deepcopy(pop[0:int(pop.shape[0]/2),:])
    pop2 = copy.deepcopy(pop[(int(pop.shape[0]/2)):(int(pop.shape[0]/2)*2),:])
    N,D = pop1.shape[0],pop1.shape[1]
    beta = np.zeros((N,D))
    mu = np.random.random_sample([N,D])
    beta[mu<=0.5]=(2*mu[mu<=0.5])**(1/(t1+1))
    beta[mu>0.5]=(2-2*mu[mu>0.5])**(-1/(t1+1))
    beta=beta*((-1)**(np.random.randint(2, size=(N,D))))
    beta[np.random.random_sample([N,D])<0.5]=1
    beta[np.tile(np.random.random_sample([N,1])>pc,(1,D))]=1
    off = np.vstack(((pop1+pop2)/2+beta*(pop1-pop2)/2,(pop1+pop2)/2-beta*(pop1-pop2)/2))
    low = pre_exp*0.001
    low = np.tile(low,(2*N,1))
    up = pre_exp*1000
    up = np.tile(up,(2*N,1))
    site = np.random.random_sample([2*N,D]) < pm/D
    mu = np.random.random_sample([2*N,D])
    temp = site & (mu<=0.5)
    off[off<low]=low[off<low]
    off[off>up]=up[off>up]
    off[temp]=off[temp]+(up[temp]-low[temp])*((2*mu[temp]+(1-2*mu[temp])*((1-(off[temp]-low[temp])/(up[temp]-low[temp]))**(t2+1)))**(1/(t2+1))-1)
    temp = site & (mu>0.5)
    off[temp]=off[temp]+(up[temp]-low[temp])*(1-(2*(1-mu[temp])+2*(mu[temp]-0.5)*((1-(up[temp]-off[temp])/(up[temp]-low[temp]))**(t2+1)))**(1/(t2+1)))
    
    return off
""" ************************************                5、 PF and Fitness Functions                       ************************************ """
def funfun(M,N,D):
    filename = 'E:/Simulation/PFR3.bkp'
    Application = win32com.client.Dispatch('Apwn.Document.40.0')
    Application.InitFromArchive2(filename)
    Application.Visible = 0
    pre_exp = []
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/1").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/2").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/3").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/4").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/5").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/6").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/7").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/8").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/9").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/10").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/11").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/12").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/13").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/14").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/15").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/16").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/17").value)
    pre_exp.append(Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/18").value)
    pre_exp = np.array(pre_exp)
    low = pre_exp*0.001
    up = pre_exp*1000
    pop = np.tile(low,(N,1))+(np.tile(up,(N,1))-np.tile(low,(N,1)))*np.random.rand(N,D)
    popfun = np.empty((0,3))
    for i in range(N):
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/1").value = pop[i][0]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/2").value = pop[i][1]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/3").value = pop[i][2]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/4").value = pop[i][3]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/5").value = pop[i][4]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/6").value = pop[i][5]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/7").value = pop[i][6]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/8").value = pop[i][7]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/9").value = pop[i][8]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/10").value = pop[i][9]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/11").value = pop[i][10]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/12").value = pop[i][11]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/13").value = pop[i][12]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/14").value = pop[i][13]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/15").value = pop[i][14]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/16").value = pop[i][15]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/17").value = pop[i][16]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/18").value = pop[i][17]
        Application.Reinit()
        Application.Run2()
        H2_1110 = Application.Tree.FindNode(r"/Data/Streams/1110SYN/Output/MOLEFRAC/MIXED/H2").value
        H2_1120 = Application.Tree.FindNode(r"/Data/Streams/1120SYN/Output/MOLEFRAC/MIXED/H2").value
        H2_1130 = Application.Tree.FindNode(r"/Data/Streams/1130SYN/Output/MOLEFRAC/MIXED/H2").value
        H2_1320 = Application.Tree.FindNode(r"/Data/Streams/1320SYN/Output/MOLEFRAC/MIXED/H2").value
        H2_1520 = Application.Tree.FindNode(r"/Data/Streams/1520SYN/Output/MOLEFRAC/MIXED/H2").value
        f1 = (((H2_1110-0.183419)**2+(H2_1120-0.1670887)**2+( H2_1130-0.1294462)**2+(H2_1320-0.276401)**2+(H2_1520-0.305148)**2)/(0.183419**2+0.1670887**2+0.1294462**2+0.276401**2+0.305148**2))**0.5
        CO_1110 = Application.Tree.FindNode(r"/Data/Streams/1110SYN/Output/MOLEFRAC/MIXED/CO").value
        CO_1120 = Application.Tree.FindNode(r"/Data/Streams/1120SYN/Output/MOLEFRAC/MIXED/CO").value
        CO_1130 = Application.Tree.FindNode(r"/Data/Streams/1130SYN/Output/MOLEFRAC/MIXED/CO").value
        CO_1320 = Application.Tree.FindNode(r"/Data/Streams/1320SYN/Output/MOLEFRAC/MIXED/CO").value
        CO_1520 = Application.Tree.FindNode(r"/Data/Streams/1520SYN/Output/MOLEFRAC/MIXED/CO").value
        f2 = (((CO_1110-0.1358131)**2+(CO_1120-0.1325502)**2+(CO_1130-0.117506)**2+(CO_1320-0.274767)**2+(CO_1520-0.437996)**2)/(0.1358131**2+0.1325502**2+0.117506**2+0.274767**2+0.437996**2))**0.5
        C_1110 = Application.Tree.FindNode(r"/Data/Streams/1110SYN/Output/MOLEFRAC/MIXED/C").value
        C_1120 = Application.Tree.FindNode(r"/Data/Streams/1120SYN/Output/MOLEFRAC/MIXED/C").value
        C_1130 = Application.Tree.FindNode(r"/Data/Streams/1130SYN/Output/MOLEFRAC/MIXED/C").value
        C_1320 = Application.Tree.FindNode(r"/Data/Streams/1320SYN/Output/MOLEFRAC/MIXED/C").value
        C_1520 = Application.Tree.FindNode(r"/Data/Streams/1520SYN/Output/MOLEFRAC/MIXED/C").value
        C_squa = ((C_1110-0.149262)**2+(C_1120-0.1267917)**2+(C_1130-0.0960206)**2+(C_1320-0.070865)**2+(C_1520-0.000179)**2)/(0.149262**2+0.1267917**2+0.0960206**2+0.070865**2+0.000179**2)
        CH4_1110 = Application.Tree.FindNode(r"/Data/Streams/1110SYN/Output/MOLEFRAC/MIXED/CH4").value
        CH4_1120 = Application.Tree.FindNode(r"/Data/Streams/1120SYN/Output/MOLEFRAC/MIXED/CH4").value
        CH4_1130 = Application.Tree.FindNode(r"/Data/Streams/1130SYN/Output/MOLEFRAC/MIXED/CH4").value
        CH4_1320 = Application.Tree.FindNode(r"/Data/Streams/1320SYN/Output/MOLEFRAC/MIXED/CH4").value
        CH4_1520 = Application.Tree.FindNode(r"/Data/Streams/1520SYN/Output/MOLEFRAC/MIXED/CH4").value
        CH4_squa = ((CH4_1110-0.0298462)**2+(CH4_1120-0.0245647)**2+(CH4_1130-0.0216441)**2+(CH4_1320-0.004614)**2+(CH4_1520)**2)/(0.0298462**2+0.0245647**2+0.0216441**2+0.004614**2)
        f3 = (C_squa + CH4_squa)**0.5
        add = [ f1,f2,f3]
        popfun = np.vstack((popfun,add))
    Application.close()
    P,nouse = uniformpoint(N,M)
    P=P/2
    return pop,popfun,P,pre_exp

def cal(pop):
    N = pop.shape[0]
    filename = 'E:/Simulation/PFR3.bkp'
    Application = win32com.client.Dispatch('Apwn.Document.40.0')
    Application.InitFromArchive2(filename)
    Application.Visible = 0
    popfun = np.empty((0,3))
    for i in range(N):
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/1").value = pop[i][0]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/2").value = pop[i][1]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/3").value = pop[i][2]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/4").value = pop[i][3]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/5").value = pop[i][4]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/6").value = pop[i][5]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/7").value = pop[i][6]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/8").value = pop[i][7]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/9").value = pop[i][8]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/10").value = pop[i][9]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/11").value = pop[i][10]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/12").value = pop[i][11]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/13").value = pop[i][12]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/14").value = pop[i][13]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/15").value = pop[i][14]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/16").value = pop[i][15]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/17").value = pop[i][16]
        Application.Tree.FindNode(r"/Data/Reactions/Reactions/COMBI/Input/PRE_EXP/18").value = pop[i][17]
        Application.Reinit()
        Application.Run2()
        H2_1110 = Application.Tree.FindNode(r"/Data/Streams/1110SYN/Output/MOLEFRAC/MIXED/H2").value
        H2_1120 = Application.Tree.FindNode(r"/Data/Streams/1120SYN/Output/MOLEFRAC/MIXED/H2").value
        H2_1130 = Application.Tree.FindNode(r"/Data/Streams/1130SYN/Output/MOLEFRAC/MIXED/H2").value
        H2_1320 = Application.Tree.FindNode(r"/Data/Streams/1320SYN/Output/MOLEFRAC/MIXED/H2").value
        H2_1520 = Application.Tree.FindNode(r"/Data/Streams/1520SYN/Output/MOLEFRAC/MIXED/H2").value
        f1 = (((H2_1110-0.183419)**2+(H2_1120-0.1670887)**2+(H2_1130-0.1294462)**2+(H2_1320-0.276401)**2+(H2_1520-0.305148)**2)/(0.183419**2+0.1670887**2+0.1294462**2+0.276401**2+0.305148**2))**0.5
        CO_1110 = Application.Tree.FindNode(r"/Data/Streams/1110SYN/Output/MOLEFRAC/MIXED/CO").value
        CO_1120 = Application.Tree.FindNode(r"/Data/Streams/1120SYN/Output/MOLEFRAC/MIXED/CO").value
        CO_1130 = Application.Tree.FindNode(r"/Data/Streams/1130SYN/Output/MOLEFRAC/MIXED/CO").value
        CO_1320 = Application.Tree.FindNode(r"/Data/Streams/1320SYN/Output/MOLEFRAC/MIXED/CO").value
        CO_1520 = Application.Tree.FindNode(r"/Data/Streams/1520SYN/Output/MOLEFRAC/MIXED/CO").value
        f2 = (((CO_1110-0.1358131)**2+(CO_1120-0.1325502)**2+(CO_1130-0.117506)**2+(CO_1320-0.274767)**2+(CO_1520-0.437996)**2)/(0.1358131**2+0.1325502**2+0.117506**2+0.274767**2+0.437996**2))**0.5
        C_1110 = Application.Tree.FindNode(r"/Data/Streams/1110SYN/Output/MOLEFRAC/MIXED/C").value
        C_1120 = Application.Tree.FindNode(r"/Data/Streams/1120SYN/Output/MOLEFRAC/MIXED/C").value
        C_1130 = Application.Tree.FindNode(r"/Data/Streams/1130SYN/Output/MOLEFRAC/MIXED/C").value
        C_1320 = Application.Tree.FindNode(r"/Data/Streams/1320SYN/Output/MOLEFRAC/MIXED/C").value
        C_1520 = Application.Tree.FindNode(r"/Data/Streams/1520SYN/Output/MOLEFRAC/MIXED/C").value
        C_squa = ((C_1110-0.149262)**2+(C_1120-0.1267917)**2+(C_1130-0.0960206)**2+(C_1320-0.070865)**2+(C_1520-0.000179)**2)/(0.149262**2+0.1267917**2+0.0960206**2+0.070865**2+0.000179**2)
        CH4_1110 = Application.Tree.FindNode(r"/Data/Streams/1110SYN/Output/MOLEFRAC/MIXED/CH4").value
        CH4_1120 = Application.Tree.FindNode(r"/Data/Streams/1120SYN/Output/MOLEFRAC/MIXED/CH4").value
        CH4_1130 = Application.Tree.FindNode(r"/Data/Streams/1130SYN/Output/MOLEFRAC/MIXED/CH4").value
        CH4_1320 = Application.Tree.FindNode(r"/Data/Streams/1320SYN/Output/MOLEFRAC/MIXED/CH4").value
        CH4_1520 = Application.Tree.FindNode(r"/Data/Streams/1520SYN/Output/MOLEFRAC/MIXED/CH4").value
        CH4_squa = ((CH4_1110-0.0298462)**2+(CH4_1120-0.0245647)**2+(CH4_1130-0.0216441)**2+(CH4_1320-0.004614)**2+(CH4_1520)**2)/(0.0298462**2+0.0245647**2+0.0216441**2+0.004614**2)
        f3 = (C_squa + CH4_squa)**0.5
        add = [f1,f2,f3]
        popfun = np.vstack((popfun,add))
    Application.close()
    return popfun

""" ************************************                      6、 IGD calculation                           ************************************ """
def EuclideanDistances(A, B):
    BT = B.transpose()
    vecProd = np.dot(A,BT)
    SqA =  A**2
    sumSqA = np.matrix(np.sum(SqA, axis=1))
    sumSqAEx = np.tile(sumSqA.transpose(), (1, vecProd.shape[1]))
 
    SqB = B**2
    sumSqB = np.sum(SqB, axis=1)
    sumSqBEx = np.tile(sumSqB, (vecProd.shape[0], 1))    
    SqED = sumSqBEx + sumSqAEx - 2*vecProd
    SqED[SqED<0]=0.0   
    ED = np.sqrt(SqED)
    return ED

def IGD(popfun,PF):
    distance = np.min(EuclideanDistances(PF,popfun),1)
    score = np.mean(distance)
    return score
