import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from utils import uniformpoint,funfun,cal,GO,envselect,IGD
import copy
import random
import win32com.client 
import csv

"""------------------------------------------  1, Configuration of Initial Parameters  ------------------------------------------"""
N_GENERATIONS = 2000                                # Number of iterations
POP_SIZE = 60                                       # Population size
M = 3                                               # Number of objectives
t1 = 15                                             # Distribution index for crossover
t2 = 20                                             # Distribution index for mutation
pc = 0.9                                            # Crossover probability
pm = 0.1                                            # Mutation probability
D = 18                                              # Number of decision variables

"""------------------------------------------          2, Data Initialization          ------------------------------------------"""
Z,N = uniformpoint(POP_SIZE,M)
pop,popfun,PF,pre_exp = funfun(M,N,D)
popfun = cal(pop)
Zmin = np.array(np.min(popfun,0)).reshape(1,M)
print("Successfully loaded data!")
plt.ion()
if M == 3:
	fig = plt.figure(figsize=plt.figaspect(0.5))
"""------------------------------------------            3, Iterative Process          ------------------------------------------"""
for i in range(N_GENERATIONS):
	print("第{name}次迭代".format(name=i+1))
	matingpool=random.sample(range(N),N)
	off = GO(pop[matingpool,:],t1,t2,pc,pm,pre_exp)
	print("Successfully generated matingpool!")
	offfun = cal(off)
	mixpop = copy.deepcopy(np.vstack((pop, off)))
	Zmin = np.array(np.min(np.vstack((Zmin,offfun)),0)).reshape(1,M)
	pop = envselect(mixpop,N,Z,Zmin,M,D)
	print("Successfully generated offsping populations!")
	popfun = cal(pop)
	plt.cla()
	if M == 3:
		fig.suptitle(" Generation=" + str(i + 1))
		ax = fig.add_subplot(1, 2, 1, projection='3d')
		fig.delaxes(fig.axes[0])
		ax.scatter(popfun[:, 0], popfun[:, 1], popfun[:, 2], color='b')
		ax2 = fig.add_subplot(1, 2, 2, projection='3d')
		ax2.view_init(10, 50)
		ax2.scatter(popfun[:, 0], popfun[:, 1], popfun[:, 2], color='b')
		if i == N_GENERATIONS - 1:
			plt.ioff()
			plt.show()
		else:
			plt.pause(0.2)
	else:
		plt.title(" Generation=" + str(i + 1))
		plt.scatter(popfun[:, 0], popfun[:, 1], color='b')
		if i == N_GENERATIONS - 1:
			plt.ioff()
			plt.scatter(popfun[:, 0], popfun[:, 1], color='b')
			plt.show()
		else:
			plt.pause(0.2)
	if (i+1) % 50 == 0:
		output = np.hstack((pop,popfun))
		file_path = f'table_output_generation_{i+1}.csv'
		table_headers = ['K1', 'K2', 'K3','K4','K5','K6','K7','K8','K9','K10','K11','K12','K13','K14','K15','K16','K17','K18','Function1','Function2','Function3',]
		print("Generating output file!")
		with open(file_path, 'w', newline='') as csv_file:
			csv_writer = csv.writer(csv_file)
			csv_writer.writerow(['Sample'] + table_headers)
			for i,row in enumerate(output,start=1):
				csv_writer.writerow([f'Sample {i}']+[str(item) for item in row])
		print("successfully saved the output file!")
print("Successfully ran the optimization process!")
