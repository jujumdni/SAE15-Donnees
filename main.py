import math
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

print("Moyenne de L1:", moyenne(L1))

ecart_type_L1 = ecart_type(L1)
print("Écart type de L1:", round(ecart_type_L1, 2))

variance_L1 = variance(L1)
print("Variance de L1:", round(variance_L1, 2))

covariance_L1_L2 = covariance(L1, L2)
print("Covariance de L1 avec L2:", round(covariance_L1_L2, 2))