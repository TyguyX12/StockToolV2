import numpy as np
from numpy.linalg import inv
import matplotlib.pyplot as plt

# train_file = "linear-regression.train.csv" #This is the homework file
train_file = "NextDayXY_10_Train.csv"
test_file = "NextDayXY_10_Test.csv"

fileData = open(train_file, "r")
SourceData = fileData.readlines()
fileData.close()

# values to setup for initialization
m = len(SourceData)  # Number of data points.
theta1 = -1
theta0 = 3
alpha = 0.01
tol = .001  # at what change of obj should the opt stop
maxiter = 5000
tolreached = 0
interationcount = maxiter

fileData = open(train_file, "r")
SourceData = fileData.readlines()

ATrial = [[0] * 2] * m
bTrial = [0] * m
aTrial = [0] * m
maxX = -10000000000000.0

for i in range(0, m):
    temp = SourceData[i].split(',')
    # print(temp)

    xval = float(temp[0])
    if (xval > maxX):
        maxX = xval
    yval = float(temp[1])
    tempList = [xval, 1]
    ATrial[i] = tempList

    aTrial[i] = xval
    bTrial[i] = yval

# print(ATrial)
# print(ATrial[len(ATrial)-1])

A = np.array(ATrial)
b = np.array(bTrial).transpose()
X = A[:, 0]
Y = b

theta = np.array([1, 0]).transpose()  # our guess y=x
AT = A.transpose()
theta = inv(AT.dot(A)).dot(AT).dot(b)
e = A.dot(theta) - b  # A x theta -b
J = (e * e).sum()  # elementwise mult of e with itself or e2 and sum
# print ('Original Matrix:')
# print(A)
# print ('Gradiant (I think):')
# print(b)
print('Sum of Least Squares: ', J)

O = []
e = (theta1 * X + theta0 - Y)
O.append((e * e).sum())
for i in range(1, maxiter):
    temp0 = theta0 - (1 / m) * alpha * sum(theta1 * X + theta0 - Y);
    temp1 = theta1 - (1 / m) * alpha * sum((theta1 * X + theta0 - Y) * X);
    theta0 = temp0;
    theta1 = temp1;
    e = (theta1 * X + theta0 - Y)
    O.append((e * e).sum())
    if (i > 1) and (abs(O[i] - O[i - 1]) < tol):
        if (abs(O[i] - O[i - 1]) < tol):
            tolreached = 1
            interationcount = i
            break;
print("Tolerance Reached: ", tolreached)
print("Iterations Performed: ", interationcount)
print("theta0: ", theta0)
print("theta1: ", theta1)
# print(O)


plt.plot(O)
plt.show()
# print(APrime)
# print((APrime[0][2]))

plt.title('Linear Regression of Sentiment Scores and Price Changes')
plt.xlabel('Sentiment Score (0 to 1)')
plt.ylabel("Percent Change")
plt.scatter(aTrial, bTrial)
plt.axline((0, theta0), slope=theta1, linewidth=2, color='r')

plt.show()
