X = (3, 1, 4, 1, 5)

mean = sum(X) / len(X)

variance = sum((x - mean) ** 2 for x in X) / len(X)

# Calculate autocovariance for lag 1
autocovariance = sum((X[i] - mean) * (X[i+1] - mean) for i in range(len(X)-1)) / (len(X)-1)
autocovariance1 = ((3-2.8)*(1-2.8) + (1-2.8)*(4-2.8) + (4-2.8)*(1-2.8) + (1-2.8)*(5-2.8) ) / (len(X)-1)

print(f"Mean: {mean}")
print(f"Variance: {variance}")
print(f"Autocovariance: {autocovariance}")
print(f"Autocovariance1: {autocovariance1}")
