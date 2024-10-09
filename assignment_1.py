# -*- coding: utf-8 -*-
"""Assignment-1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1VZRpgB4kL1XrAvJ-mBYHPJ4KfeW4m_ZX
"""

# Headers

import numpy as np
import pandas as pd
import os
import scipy.stats
from sklearn.metrics import confusion_matrix, f1_score, accuracy_score, roc_curve, auc
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

"""# Question 1

## Data
"""

# Generating samples

P_L0 = 0.35
P_L1 = 0.65

mu_0 = [-1, -1, -1, -1]
sigma_0 = [[2, -0.5, 0.3, 0], [-0.5, 1, -0.5, 0], [0.3, -0.5, 1, 0], [0, 0, 0, 2]]
mu_1 = [1, 1, 1, 1]
sigma_1 = [[1, 0.3, -0.2, 0], [0.3, 2, 0.3, 0], [-0.2, 0.3, 1, 0], [0, 0, 0, 3]]

N = 10000

samples = np.zeros((N, 4))
L_samples = np.random.choice([0, 1], size=N, p=[P_L0, P_L1])
for i in range(N):
  if L_samples[i] == 0:
    samples[i] = np.random.multivariate_normal(mu_0, sigma_0)
  if L_samples[i] == 1:
    samples[i] = np.random.multivariate_normal(mu_1, sigma_1)

# Convert samples to a DataFrame for easier plotting with seaborn

df = pd.DataFrame(samples, columns=['Dim1', 'Dim2', 'Dim3', 'Dim4'])
df['L'] = L_samples

df.head()

# Plotting probability density functions for different dimensions

for i, dim in enumerate(['Dim1', 'Dim2', 'Dim3', 'Dim4']):
    plt.subplot(2, 2, i + 1)  # Create a 2x2 grid of subplots
    sns.kdeplot(data=df, x=dim, hue='L', palette={0: 'blue', 1: 'red'}, fill=True)
    plt.title(f'Distribution of {dim}')
    plt.xlabel(dim)

plt.tight_layout()
plt.show()

"""## Classification"""

# Classification function

def likelihood_ratio_test(x, m0, m1, C0, C1, gamma):
  p_x_given_L0 = scipy.stats.multivariate_normal.pdf(x, mean=m0, cov=C0)
  p_x_given_L1 = scipy.stats.multivariate_normal.pdf(x, mean=m1, cov=C1)
  L_ratio = p_x_given_L1/p_x_given_L0
  return L_ratio > gamma

# Part A: ERM Classification using correct data distribution
# Calculating the TPR(True Positive Rate) and FPR(False Positive Rate)

gamma_values = np.logspace(-10, 10, num=1000)
ERM_mu_0 = [-1, -1, -1, -1]
ERM_sigma_0 = [[2, -0.5, 0.3, 0], [-0.5, 1, -0.5, 0], [0.3, -0.5, 1, 0], [0, 0, 0, 2]]
ERM_mu_1 = [1, 1, 1, 1]
ERM_sigma_1 = [[1, 0.3, -0.2, 0], [0.3, 2, 0.3, 0], [-0.2, 0.3, 1, 0], [0, 0, 0, 3]]

TPR = []
FPR = []

for gamma in gamma_values:
  D = likelihood_ratio_test(samples, ERM_mu_0, ERM_mu_1, ERM_sigma_0, ERM_sigma_1, gamma)
  TP = np.sum((D == True) & (L_samples == 1))
  FN = np.sum((D == False) & (L_samples == 1))
  FP = np.sum((D == True) & (L_samples == 0))
  TN = np.sum((D == False) & (L_samples == 0))

  TPR.append(TP/(TP+FN))
  FPR.append(FP/(FP+TN))

# Part B: ERM Classification using incorrect data distribution
# Calculating the TPR(True Positive Rate) and FPR(False Positive Rate)

gamma_values = np.logspace(-10, 10, num=1000)
ERM_mu_0 = [-1, -1, -1, -1]
ERM_sigma_0 = [[2, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 2]]
ERM_mu_1 = [1, 1, 1, 1]
ERM_sigma_1 = [[1, 0, 0, 0], [0, 2, 0, 0], [0, 0, 1, 0], [0, 0, 0, 3]]

TPR = []
FPR = []

for gamma in gamma_values:
  D = likelihood_ratio_test(samples, ERM_mu_0, ERM_mu_1, ERM_sigma_0, ERM_sigma_1, gamma)
  TP = np.sum((D == True) & (L_samples == 1))
  FN = np.sum((D == False) & (L_samples == 1))
  FP = np.sum((D == True) & (L_samples == 0))
  TN = np.sum((D == False) & (L_samples == 0))

  TPR.append(TP/(TP+FN))
  FPR.append(FP/(FP+TN))

# Part C: ERM Classification using Fisher LDA
# Calculating the TPR(True Positive Rate) and FPR(False Positive Rate)

samples_L0 = samples[L_samples == 0]
samples_L1 = samples[L_samples == 1]

# rowvar specifies that columns are features and rows are data points
# in SW we multiply by (samples_L0.shape[0] - 1) to reverse normalize
# in SB we reshape to convert into column and row vectors
LDA_overall_mean = np.mean(samples, axis=0)
LDA_mu_0 = np.mean(samples_L0, axis=0)
LDA_mu_1 = np.mean(samples_L1, axis=0)
LDA_sigma_0 = np.cov(samples_L0, rowvar=False)
LDA_sigma_1 = np.cov(samples_L1, rowvar=False)
# SW = LDA_sigma_0*(samples_L0.shape[0]-1)+LDA_sigma_1*(samples_L1.shape[0]-1)
SW = LDA_sigma_0+LDA_sigma_1
# SB = (LDA_mu_0-LDA_overall_mean).reshape(-1, 1)@(LDA_mu_0-LDA_overall_mean).reshape(1, -1)*samples_L0.shape[0] + (LDA_mu_1-LDA_overall_mean).reshape(-1, 1)@(LDA_mu_1-LDA_overall_mean).reshape(1, -1)*samples_L1.shape[0]
SB = (LDA_mu_0-LDA_overall_mean).reshape(-1, 1)@(LDA_mu_0-LDA_overall_mean).reshape(1, -1) + (LDA_mu_1-LDA_overall_mean).reshape(-1, 1)@(LDA_mu_1-LDA_overall_mean).reshape(1, -1)

# Generalized eigendecomposition
eigenvalues, eigenvectors = np.linalg.eig(np.linalg.inv(SW)@SB)
sorted_indices = np.argsort(eigenvalues)[::-1]
LDA_w = eigenvectors[:, sorted_indices[0]]

# Projecting samples onto largest eigenvector
projected_samples = samples @ LDA_w
thresholds = np.linspace(np.min(projected_samples), np.max(projected_samples), 1000)
TPR = []
FPR = []
for t in thresholds:
  predictions = (projected_samples > t)
  TP = np.sum((predictions == True) & (L_samples == 1))
  FN = np.sum((predictions == False) & (L_samples == 1))
  FP = np.sum((predictions == True) & (L_samples == 0))
  TN = np.sum((predictions == False) & (L_samples == 0))

  TPR.append(TP/(TP+FN))
  FPR.append(FP/(FP+TN))

"""## Result Visualization"""

# Calculating Empirical and Theoretical Optimal Threshold

fpr = np.array(FPR)
tpr = np.array(TPR)

P_error = fpr*P_L0 + (1-tpr)*P_L1
min_error_index = np.argmin(P_error)
print(f'Empirical optimal threshold: {gamma_values[min_error_index]}')
print(f'Minimum probability of error: {P_error[min_error_index]}')
print(f'Assuming the cost of errors is the same')
print(f'Theoretical optimal threshold: {P_L0/P_L1}')

# Plotting ROC and computing AUROC

plt.figure(figsize=(8, 6))
plt.plot(FPR, TPR, label="ROC Curve")
plt.scatter(fpr[min_error_index], tpr[min_error_index], color='red', label='Min P(error) threshold', marker = 'o', s=100)
plt.xlabel("False Positive Rate (FPR)")
plt.ylabel("True Positive Rate (TPR)")
plt.title("ROC Curve for Classifier")
plt.grid(True)
plt.legend()
plt.show()

print(f'Area under ROC: {auc(FPR, TPR)}')

"""# Question 2

## Data
"""

# Generating samples

P_L1 = 0.30
P_L2 = 0.30
P_L3 = 0.40

mu_1 = [0, 0, 0]
sigma_1 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
mu_2 = [2, 0, 0]
sigma_2 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
mu_3 = [0, 2, 0]
sigma_3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
mu_4 = [0, 2, 2]
sigma_4 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

N = 10000

samples = np.zeros((N, 3))
L_samples = np.random.choice([1, 2, 3], size=N, p=[P_L1, P_L2, P_L3])
for i in range(N):
  if L_samples[i] == 1:
    samples[i] = np.random.multivariate_normal(mu_1, sigma_1)
  if L_samples[i] == 2:
    samples[i] = np.random.multivariate_normal(mu_2, sigma_2)
  if L_samples[i] == 3:
    a = np.random.choice([0, 1], p=[0.5, 0.5])
    if a == 0:
      samples[i] = np.random.multivariate_normal(mu_3, sigma_3)
    else:
      samples[i] = np.random.multivariate_normal(mu_4, sigma_4)

# Visualize samples

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(samples[L_samples == 1][:, 0], samples[L_samples == 1][:, 1], samples[L_samples == 1][:, 2], color='r', label='Class 1', alpha=0.5)
ax.scatter(samples[L_samples == 2][:, 0], samples[L_samples == 2][:, 1], samples[L_samples == 2][:, 2], color='g', label='Class 2', alpha=0.5)
ax.scatter(samples[L_samples == 3][:, 0], samples[L_samples == 3][:, 1], samples[L_samples == 3][:, 2], color='b', label='Class 3', alpha=0.5)
ax.set_xlabel('X1')
ax.set_ylabel('X2')
ax.set_zlabel('X3')
ax.legend()
plt.title('Samples from Mixture of 4 Gaussians')
plt.show()

"""## Part A: MPE Classifier"""

# Classification based on max posterior probability

def MPE_classifier(x):
  post_L1 = P_L1 * scipy.stats.multivariate_normal.pdf(x, mean=mu_1, cov=sigma_1)
  post_L2 = P_L2 * scipy.stats.multivariate_normal.pdf(x, mean=mu_2, cov=sigma_2)
  post_L3 = P_L3 * (0.5*scipy.stats.multivariate_normal.pdf(x, mean=mu_3, cov=sigma_3) + 0.5*scipy.stats.multivariate_normal.pdf(x, mean=mu_1, cov=sigma_1))
  return np.argmax(np.stack([post_L1, post_L2, post_L3], axis=1), axis=1)+1

D_samples = np.array([MPE_classifier(samples)])

# Confusion Matrix

confusion_matrix = np.zeros((3, 3))
correct_assignments = 0
total_samples = 0
for i in range(1, 4):
  for j in range(1, 4):
    confusion_matrix[i-1, j-1] = np.sum((L_samples == i) & (D_samples == j)) / np.sum(L_samples == i)
    if i == j:
      correct_assignments += np.sum((L_samples == i) & (D_samples == j))
plt.figure(figsize=(8, 6))
sns.heatmap(confusion_matrix, annot=True, cmap='Blues', fmt='.2f', xticklabels=[f'D={i}' for i in range(1, 4)], yticklabels=[f'L={i}' for i in range(1, 4)])
plt.title('Confusion Matrix Heatmap')
plt.xlabel('Predicted label')
plt.ylabel('True label')
plt.show()
print(f'Accuracy: {correct_assignments/10000}')

# Visualization of data

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
markers = {1: 'x', 2: 'o', 3: '^'}
for i in range(1, 4):
  correct_idx = (L_samples == i) & (L_samples == D_samples.reshape(-1))
  incorrect_idx = (L_samples == i) & (L_samples != D_samples.reshape(-1))
  ax.scatter(samples[correct_idx, 0], samples[correct_idx, 1], samples[correct_idx, 2], c='green', marker=markers[i], label=f'Class {i} Correct', alpha = 0.3)
  ax.scatter(samples[incorrect_idx, 0], samples[incorrect_idx, 1], samples[incorrect_idx, 2], c='red', marker=markers[i], label=f'Class {i} Incorrect', alpha = 0.3)
ax.set_xlabel('X1')
ax.set_ylabel('X2')
ax.set_zlabel('X3')
ax.legend()
plt.title('Plot with Classification Result')
plt.show()

"""## Part B: ERM Classification"""

# ERM Classification

def ERM_classifier(x, loss_matrix):
  post_L1 = scipy.stats.multivariate_normal.pdf(x, mean=mu_1, cov=sigma_1)
  post_L2 = scipy.stats.multivariate_normal.pdf(x, mean=mu_2, cov=sigma_2)
  post_L3 = (0.5*scipy.stats.multivariate_normal.pdf(x, mean=mu_3, cov=sigma_3) + 0.5*scipy.stats.multivariate_normal.pdf(x, mean=mu_1, cov=sigma_1))
  risks = np.zeros((samples.shape[0], 3))
  for i in range(3):
    risks[:, i] = np.dot(np.stack([post_L1, post_L2, post_L3], axis=1), loss_matrix[i, :])
  D_samples = np.argmin(risks, axis=1)+1
  return D_samples

Lambda_1 = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]])
Lambda_10 = np.array([[0, 10, 10], [1, 0, 10], [1, 1, 0]])
Lambda_100 = np.array([[0, 100, 100], [1, 0, 100], [1, 1, 0]])
D_samples_1 = ERM_classifier(samples, Lambda_1)
D_samples_10 = ERM_classifier(samples, Lambda_10)
D_samples_100 = ERM_classifier(samples, Lambda_100)

# Expected Risk

confusion_matrix_1 = np.zeros((3, 3))
confusion_matrix_10 = np.zeros((3, 3))
confusion_matrix_100 = np.zeros((3, 3))
correct_assignments_1 = 0
correct_assignments_10 = 0
correct_assignments_100 = 0

for i in range(1, 4):
  for j in range(1, 4):
    confusion_matrix_1[i-1, j-1] = np.sum((L_samples == i) & (D_samples_1 == j)) / np.sum(L_samples == i)
    confusion_matrix_10[i-1, j-1] = np.sum((L_samples == i) & (D_samples_10 == j)) / np.sum(L_samples == i)
    confusion_matrix_100[i-1, j-1] = np.sum((L_samples == i) & (D_samples_100 == j)) / np.sum(L_samples == i)
    if i == j:
      correct_assignments_1 += np.sum((L_samples == i) & (D_samples_1 == j))
      correct_assignments_10 += np.sum((L_samples == i) & (D_samples_10 == j))
      correct_assignments_100 += np.sum((L_samples == i) & (D_samples_100 == j))

print(f'Expected Risk with Lambda_1: {np.sum(confusion_matrix_1*Lambda_1)}')
print(f'Expected Risk with Lambda_10: {np.sum(confusion_matrix_10*Lambda_10)}')
print(f'Expected Risk with Lambda_100: {np.sum(confusion_matrix_100*Lambda_100)}')

plt.figure(figsize=(8, 6))
sns.heatmap(confusion_matrix_1, annot=True, cmap='Blues', fmt='.2f', xticklabels=[f'D={i}' for i in range(1, 4)], yticklabels=[f'L={i}' for i in range(1, 4)])
plt.title('Confusion Matrix Heatmap')
plt.xlabel('Predicted label')
plt.ylabel('True label')
plt.show()
print(f'Accuracy: {correct_assignments_1/10000}')

plt.figure(figsize=(8, 6))
sns.heatmap(confusion_matrix_10, annot=True, cmap='Blues', fmt='.2f', xticklabels=[f'D={i}' for i in range(1, 4)], yticklabels=[f'L={i}' for i in range(1, 4)])
plt.title('Confusion Matrix Heatmap')
plt.xlabel('Predicted label')
plt.ylabel('True label')
plt.show()
print(f'Accuracy: {correct_assignments_10/10000}')

plt.figure(figsize=(8, 6))
sns.heatmap(confusion_matrix_100, annot=True, cmap='Blues', fmt='.2f', xticklabels=[f'D={i}' for i in range(1, 4)], yticklabels=[f'L={i}' for i in range(1, 4)])
plt.title('Confusion Matrix Heatmap')
plt.xlabel('Predicted label')
plt.ylabel('True label')
plt.show()
print(f'Accuracy: {correct_assignments_100/10000}')

"""# Question 3

## Data
"""

!pip install ucimlrepo

# Data 1

from ucimlrepo import fetch_ucirepo

wine_quality = fetch_ucirepo(id=186)
X = wine_quality.data.features
y = wine_quality.data.targets

wine_quality.data.original.head()

# Data 2
# Not considering subjects as either features or labels

file_path = '/content/drive/MyDrive/EECE 5644/Assignment-1/UCI HAR Dataset'

features = pd.read_csv(os.path.join(file_path, 'features.txt'), sep='\s+', header=None)
activity_labels = pd.read_csv(os.path.join(file_path, 'activity_labels.txt'), sep='\s+', header=None)

train_data = pd.read_csv(os.path.join(file_path, 'train/X_train.txt'), sep='\s+', header=None)
train_labels = pd.read_csv(os.path.join(file_path, 'train/y_train.txt'), sep='\s+', header=None)
# train_subjects = pd.read_csv(os.path.join(file_path, 'train/subject_train.txt'), sep='\s+', header=None)

test_data = pd.read_csv(os.path.join(file_path, 'test/X_test.txt'), sep='\s+', header=None)
test_labels = pd.read_csv(os.path.join(file_path, 'test/y_test.txt'), sep='\s+', header=None)
# test_subjects = pd.read_csv(os.path.join(file_path, 'test/subject_test.txt'), sep='\s+', header=None)

# Convert to numpy arrays
# Data 1

X = X.values
y = y.values.reshape(-1)

# Convert to numpy arrays
# Data 2

X_train = train_data.values
y_train = train_labels.values.reshape(-1)
X_test = test_data.values
y_test = test_labels.values.reshape(-1)

"""## Classification"""

# MPE Classifier
# For regularization, geometric mean of non-zero eigenvalues gives best result
# For non-zero eigenvalues, eigenvalues > 0 gives errors, eigenvalues > 1e-10 does not
# c_const = 0.1 gives best F1 score
# Vectorized map was used to get back the original classes from idx

def MPE_Classifier(X_train, y_train, X_test, y_test, c_const=1e-1, epsilon=1e-10, reg_method='geometric mean'):
  classes = np.unique(y_train)
  n_samples = X_test.shape[0]
  n_features = X_test.shape[1]
  n_classes = len(classes)

  means = {}
  covariances = {}
  priors = {}
  for cls in classes:
    X_cls = X_train[y_train == cls]
    means[cls] = np.mean(X_cls, axis=0)
    cov_matrix = np.cov(X_cls, rowvar=False)
    eigenvalues, _ = np.linalg.eigh(cov_matrix)
    nonzero_eigenvalues = eigenvalues[eigenvalues > 1e-10]
    if reg_method == 'geometric mean':
      reg_const = c_const * np.exp(np.mean(np.log(nonzero_eigenvalues)))
    elif reg_method == 'arithmetic mean':
      reg_const = c_const * np.mean(nonzero_eigenvalues)
    else:
      reg_const = c_const
    covariances[cls] = cov_matrix + reg_const * np.eye(cov_matrix.shape[0])
    priors[cls] = X_cls.shape[0]/X_train.shape[0]

  discriminants = np.zeros((n_samples, n_classes))
  for idx, cls in enumerate(classes):
    discriminants[:, idx] = np.log(scipy.stats.multivariate_normal.pdf(X_test, means[cls], covariances[cls])+epsilon)+np.log(priors[cls]+epsilon)
  predicted_classes = np.argmax(discriminants, axis=1)

  def map_value(x):
    for idx, cls in enumerate(classes):
      if x == idx:
        return cls
  vectorized_map = np.vectorize(map_value)
  predicted_classes = vectorized_map(predicted_classes)

  return predicted_classes

# Standardize the data
# Data 1
# X gives better result than X_scaled

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
# y_pred = MPE_Classifier(X_scaled, y)
y_pred = MPE_Classifier(X, y, X, y, 1e-2, 1e-10, 'none')

# Standardize the data
# Data 2
# X gives better result than X_scaled

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.fit_transform(X_test)
# y_pred = MPE_Classifier(X_train_scaled, y_train, X_test_scaled, y_test)
y_pred = MPE_Classifier(X_train, y_train, X_test, y_test, 1e-1, 1e-10, 'arithmetic mean')
X = X_test
y = y_test

"""## Result Visualization"""

# Confusion Matrix

classes = np.unique(y)
sns.heatmap(confusion_matrix(y, y_pred), annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.title('Confusion Matrix')
plt.show()

# F1 Score and Error Probability Estimate

print(f"F1 score (Weighted): {f1_score(y, y_pred, average='weighted')}")
print(f"Error Probability Estimate: {1 - accuracy_score(y, y_pred)}")

# Visualizing principal components for data

pca = PCA(n_components=2)
# X_pca = pca.fit_transform(X_scaled)
X_pca = pca.fit_transform(X)
print("Amount of variance associated with each component:", pca.explained_variance_ratio_)
plt.figure(figsize=(8, 6))
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y, edgecolor='k', cmap='viridis')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('PCA Result')
plt.colorbar(label='Class Label')
plt.grid()
plt.show()