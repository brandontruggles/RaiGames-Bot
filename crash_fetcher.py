import hashlib
import hmac
import math
import csv
import os
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsRegressor

def getPrevHash(currHash):
	prevHash = hashlib.sha256()
	prevHash.update(currHash)
	return prevHash.hexdigest().encode("utf-8")

def hmacDivisible(hmacHash, mod):
	val = 0

	o = len(hmacHash) % 4

	i = o - 4 if o > 0 else 0	

	while i < len(hmacHash):
		val = ((val << 16) + int(hmacHash[i : i + 4], 16)) % mod
		i += 4 

	return (val == 0)

def getCrashFromHash(currHash):
	hmacCalculator = hmac.new(currHash, digestmod=hashlib.sha256)
	hmacCalculator.update(b"000000000000000007a9a31ff7f07463d91af6b5454241d5faf282e5e0fe1b3a")
	hmacHash = hmacCalculator.hexdigest().encode("utf-8").decode()
	if hmacDivisible(hmacHash, 101):
		return 0
	h = int(hmacHash[0 : 13], 16)
	e = math.pow(2, 52)
	return (math.floor((100 * e - h) / (e - h)) / 100)

limit = 100000
gameHash = input("Please enter a game hash to start with: ").encode("utf-8")
print("Writing past crashes to 'crashes.txt'...")
currHash = gameHash
outputFile = open(os.path.join(os.path.dirname(__file__), "crashes.csv"), "w")
csvWriter = csv.writer(outputFile)
csvWriter.writerow(["Game Hash", "Crash"])
for i in range(limit):
	csvWriter.writerow([currHash.decode(), str(getCrashFromHash(currHash))])
	currHash = getPrevHash(currHash)
outputFile.close()
print("Write complete!")

crashes = pd.read_csv(os.path.join(os.path.dirname(__file__), "crashes.csv")) 
crashes = crashes.query("Crash < 10") 
crashes = crashes.assign(Time=list(range(len(crashes))), Normalized_Crash=crashes["Crash"].apply(np.floor)) 
 
regressor = KNeighborsRegressor(n_neighbors=20) 
attributes = crashes["Time"].values.reshape(-1, 1) 
labels = crashes["Crash"] 
train_x = attributes[:-44000] 
test_x = attributes[-44000:] 
train_y = labels[:-44000] 
test_y = labels[-44000:] 
regressor.fit(train_x, train_y) 
prediction = regressor.predict(test_x)
print(prediction) 
plt.scatter(test_x, test_y, color="black") 
plt.plot(test_x, prediction, color="blue", linewidth=3) 
plt.show()
