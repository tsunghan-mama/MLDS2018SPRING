from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn import datasets, manifold
import matplotlib.pyplot as plt
import numpy as np

def read_data(x, dim):
	return np.loadtxt(x).reshape(-1, dim)

def pca(X, n_components):
    pca = PCA(n_components = n_components)
    pca.fit(X)
    return pca.transform(X)
###########################
times = 8
dim = 16750
###########################
file_name = ["csvdir/L1_" + str(x) + ".csv" for x in range(1, times+1)]
loss_file = ["csvdir/acc_" + str(x) + ".csv" for x in range(1, times+1)]
param = [read_data(x, dim) for x in file_name]
loss = [read_data(x, 1) for x in loss_file]
loss = [np.around(x, 2) for x in loss]

# param = [StandardScaler().fit_transform(x) for x in param]
# tsne = manifold.TSNE(n_components=2, init='pca', random_state=0)
pca = PCA(n_components=2)

param = [pca.fit_transform(x) for x in param]
# param = [tsne.fit_transform(x) for x in param]
print (pca.singular_values_)

color = ["red", "orange", "lime", "green", "blue", "purple", "cyan", "pink"]
# plt.figure(figsize=(10,7))
# plt.xlabel("label1")
# plt.ylabel("label2")
# for x, y in zip(param, color):
# 	plt.scatter(x[:,0], x[:,1], s=0.7, color=y, marker=acc[0])
# plt.show()
index = 0

fig, ax = plt.subplots()
ax.set_xlabel(r'$label_{1}$', fontsize=14)
ax.set_ylabel(r'$label_{2}$', fontsize=14)
ax.set_title('Layer 1', fontsize=18)

for x, y in zip(param, loss):
	ax.scatter(x[:,0], x[:,1], s=0.2, color=color[index])
	for i in range(0, y.shape[0], 10):
		ax.annotate(y[i][0], (x[:,0][i],x[:,1][i]), fontsize=4, color=color[index])
	index += 1

plt.show()
