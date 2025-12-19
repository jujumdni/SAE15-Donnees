import math
import matplotlib.pyplot as plt
import numpy as np

T=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23] 
L1=[3,3,4,3,2,5,8,9,13,16,18,18,19,21,22,22,21,17,17,12,10,8,7,4] 
L2=[103,203,4,3,2,5,8,9,13,16,18,18,19,21,22,22,21,17,17,12,10,-92,-93,-96]

def moyenne(L):
    return sum(L)/len(L)

def ecart_type(L):
    m = moyenne(L)
    variance = sum((x - m) ** 2 for x in L) / len(L)
    return math.sqrt(variance)

def variance(L):
    m = moyenne(L)
    return sum((x - m) ** 2 for x in L) / len(L)

def covariance(LX, LY):
    mx = moyenne(LX)
    my = moyenne(LY)
    return sum((x - mx) * (y - my) for x, y in zip(LX, LY)) / len(LX)

def coefficient_correlation(LX, LY):
    cov = covariance(LX, LY)
    std_x = ecart_type(LX)
    std_y = ecart_type(LY)
    return cov / (std_x * std_y)

def matrice_correlation(LX, LY):
    return [[1, coefficient_correlation(LX, LY)],
            [coefficient_correlation(LY, LX), 1]]

def graphique_evolution(T, L, titre="Évolution de la grandeur", xlabel="Temps", ylabel="Valeur"):
    plt.figure(figsize=(10, 6))
    plt.plot(T, L, marker='o', linestyle='-', linewidth=2)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(titre)
    plt.grid(True)
    plt.show()

def heatmap_correlations(listes, noms=None):
    n = len(listes)
    matrice = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i == j:
                matrice[i][j] = 1
            else:
                matrice[i][j] = coefficient_correlation(listes[i], listes[j])
    
    if noms is None:
        noms = [f"Liste {i+1}" for i in range(n)]
    
    plt.figure(figsize=(8, 6))
    plt.imshow(matrice, cmap='coolwarm', vmin=-1, vmax=1)
    plt.colorbar(label='Coefficient de corrélation')
    plt.xticks(range(n), noms, rotation=45)
    plt.yticks(range(n), noms)
    plt.title('Heatmap des corrélations')
    
    for i in range(n):
        for j in range(n):
            plt.text(j, i, f'{matrice[i][j]:.2f}', ha='center', va='center', color='black')
    
    plt.tight_layout()
    plt.show()

print("Moyenne de L1:", moyenne(L1))

print("Écart type de L1:", round(ecart_type(L1), 2))

print("Variance de L1:", round(variance(L1), 2))

print("Covariance de L1 avec L2:", round(covariance(L1, L2), 2))

print("Coefficient de corrélation de L1 avec L2:", round(coefficient_correlation(L1, L2), 2))

print("Matrice de corrélation entre L1 et L2:")
matrice = matrice_correlation(L1, L2)
for row in matrice:
    print(row)

graphique_evolution(T, L1, "Évolution de L1 en fonction du temps", "Temps (heures)", "L1")

heatmap_correlations([T, L1, L2], ['T', 'L1', 'L2'])