# -*- coding: utf-8 -*-
"""tensorflow.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zn_jeT-O1EEf_pIqtdEILPHtdqyJSR9x
"""

import torch, torchvision
from torch import nn
from torch import optim
from torchvision.transforms import ToTensor
import torch.nn.functional as F
import matplotlib.pyplot as plt

import requests
from PIL import Image
from io import BytesIO

import copy

from sklearn.metrics import confusion_matrix
import pandas as pd
import numpy as np

numb_batch = 64

T = torchvision.transforms.Compose([
    torchvision.transforms.ToTensor()
])
train_data = torchvision.datasets.MNIST('mnist_data', train=True, download=True, transform=T)
val_data = torchvision.datasets.MNIST('mnist_data', train=False, download=True, transform=T)

train_dl = torch.utils.data.DataLoader(train_data, batch_size = numb_batch)
val_dl = torch.utils.data.DataLoader(val_data, batch_size = numb_batch)

def create_lenet():
    model = nn.Sequential(
        nn.Conv2d(1, 6, 5, padding=2),
        nn.ReLU(),
        nn.AvgPool2d(2, stride=2),
        nn.Conv2d(6, 16, 5, padding=0),
        nn.ReLU(),
        nn.AvgPool2d(2, stride=2),
        nn.Flatten(),
        nn.Linear(400, 120),
        nn.ReLU(),
        nn.Linear(120, 84),
        nn.ReLU(),
        nn.Linear(84, 10)
    )
    return model

def validate(model, data):
    total = 0
    correct = 0
    for i, (images, labels) in enumerate(data):
        images = images.cuda()
        x = model(images)
        value, pred = torch.max(x,1)
        pred = pred.data.cpu()
        total += x.size(0)
        correct += torch.sum(pred == labels)
    return correct*100./total

def train(numb_epoch=3, lr=1e-3, device="cpu"):
    accuracies = []
    cnn = create_lenet().to(device)
    cec = nn.CrossEntropyLoss()
    optimizer = optim.Adam(cnn.parameters(), lr=lr)
    max_accuracy = 0
    for epoch in range(numb_epoch):
        for i, (images, labels) in enumerate(train_dl):
            images = images.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            pred = cnn(images)
            loss = cec(pred, labels)
            loss.backward()
            optimizer.step()
        accuracy = float(validate(cnn, val_dl))
        accuracies.append(accuracy)
        if accuracy > max_accuracy:
            best_model = copy.deepcopy(cnn)
            max_accuracy = accuracy
            print("Saving Best Model with Accuracy: ", accuracy)
        print('Epoch:', epoch+1, "Accuracy :", accuracy, '%')
    plt.plot(accuracies)
    return best_model

if torch.cuda.is_available():
    device = torch.device("cuda:0")
else:
    device = torch.device("cpu")
    print("No Cuda Available")

device

lenet = train(40, device=device)

torch.save(lenet.state_dict(), "lenet.pth")

lenet = create_lenet().to(device)
lenet.load_state_dict(torch.load("lenet.pth"))
lenet.eval()

def predict_dl(model, data):
    y_pred = []
    y_true = []
    for i, (images, labels) in enumerate(data):
        images = images.cuda()
        x = model(images)
        value, pred = torch.max(x, 1)
        pred = pred.data.cpu()
        y_pred.extend(list(pred.numpy()))
        y_true.extend(list(labels.numpy()))
    return np.array(y_pred), np.array(y_true)

y_pred, y_true = predict_dl(lenet, val_dl)

pd.DataFrame(confusion_matrix(y_true, y_pred, labels=np.arange(0,10)))

def inference(path, model, device):
    r = requests.get(path)
    with BytesIO(r.content) as f:
        img = Image.open(f).convert(mode="L")
        img = img.resize((28, 28))
        x = (255 - np.expand_dims(np.array(img), -1))/255.
    with torch.no_grad():
        pred = model(torch.unsqueeze(T(x), axis=0).float().to(device))
        return F.softmax(pred, dim=-1).cpu().numpy()

path = "https://w7.pngwing.com/pngs/871/395/png-transparent-number-4-number-angle-number-4-4-number-thumbnail.png"
r = requests.get(path)
with BytesIO(r.content) as f:
    img = Image.open(f).convert(mode="L")
    img = img.resize((28, 28))
x = (255 - np.expand_dims(np.array(img), -1))/255.

plt.imshow(x.squeeze(-1), cmap="gray")

pred = inference(path, lenet, device=device)
pred_idx = np.argmax(pred)
print(f"Predicted: {pred_idx}, Prob: {pred[0][pred_idx]*100} %")

pred

#Gradient Descent Function
def gradient_descent(X_train, y, lbd, alp, max_iter, costs):
  pheta = np.zeros(X_train.shape[1])
  cost = []

  for i in range(max_iter):
    j = np.dot(X_train, pheta)
    k = 1 / (1 + np.exp(-j))

    regu = lbd / y.size * pheta
    regu[0] = 0
    cst = (-y * np.log(k) - (1 - y) * np.log(1 - k)).mean()
    grad = np.dot(X_train.T, (k - y)) / y.size + regu
    pheta = pheta - alp * grad

    if i%100 == 0:
      cost.append(cst)
  
  return pheta, cost

#Predict Function
def predict(X_test, pheta):
  i = np.dot(X_test, pheta)
  ans = 1 / (1 + np.exp(-i))
  return ans

#Logistic Regression Function
def lr(X_train, X_test, y_train):
  train_inter = np.ones((X_train.shape[0], 1))
  test_inter = np.ones((X_test.shape[0], 1))
  X_train = np.concatenate((train_inter, X_train), axis = 1)
  X_test = np.concatenate((test_inter, X_test), axis = 1)
  i = set(y_train)
  j = []
  k = []

  lbd = 0
  alp = 0.2
  max_iter = 10000
  costs = False

  for l in i:
    y_temp = np.array(y_train == l, dtype = int)
    pheta, cost = gradient_descent(X_train, y_temp, lbd, alp, max_iter, costs)
    
    j.append(pheta)
    k.append(cost)

  #Probabilities
  test_predict = np.zeros((len(i), len(X_test)))
  for m in range(len(i)):
    test_predict[m,:] = predict(X_test, j[m]) 

  train_predict = np.zeros((len(i), len(X_train)))
  for n in range(len(i)):
    train_predict[n,:] = predict(X_train, y[n]) 

  #Max Probabilities
  y_test_predict = np.argmax(test_predict, axis = 0)
  y_train_predict = np.argmax(train_predict, axis = 0)

  #Solution
  results = {"Costs": cost, "y_test_predict": y_test_predict, "y_train_predict": y_train_predict, "learning_rate": alp, "max_iterations": max_iter, "lambda": lbd}

  return results


def kfoldCV(df, f):
  data = cross_validation_split(df, f)
  sol = []

  #Creating train and test sets
  for i in range(f):
    j = list(range(f))
    j.pop(i)
    for k in j:
      if k == j[0]:
        l = data[k]
      else:
        l = np.concatenate((l, data[k]), axis = 0)
    
    m = lr(l[:, 0:X_train.shape[1]], data[i][:, 0:X_train.shape[1]], l[:, X_train.shape[1]])
    n = m['y_predict']

    #Accuracy Calculation
    acc = (n == data[i][:, X_train.shape[1]]).sum()
    sol.append(acc / len(n))

  return sol


def cross_validation_split(df, f):
  split_data = []
  data = df
  f_shape = int(data.copy.shape[0] / f)

  #save folds
  for i in range(f):
    fold = []
    while len(fold) < f_shape:
      j = randrange(data.shape[0])
      k = data.index[j]
      fold.append(data.loc[k].values.tolist())
      data = data.drop(k)
    split_data.append(np.asarray(fold))

  return split_data