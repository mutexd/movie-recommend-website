import numpy as np
from scipy.optimize import fmin_cg

def costFunction(params, Y, R, num_users, num_movies, num_features, l):
    # reshape params into X and Theta
    X = np.reshape(params[0:num_movies*num_features], (num_movies, num_features))
    Theta = np.reshape(params[num_movies*num_features:], (num_users, num_features))

    # calculate Cost
    H = (np.dot(X,Theta.transpose()) - Y) * R
    J = sum(sum(H ** 2)) / 2 + (l/2)*sum(sum(Theta ** 2)) + (l/2)*sum(sum(X **2))
    return J

def gradientStep(params, Y, R, num_users, num_movies, num_features, l):
    # reshape params into X and Theta
    X = np.reshape(params[0:num_movies*num_features], (num_movies, num_features))
    Theta = np.reshape(params[num_movies*num_features:], (num_users, num_features))

    # calculate Gradient
    H = (np.dot(X,Theta.transpose()) - Y) * R
    X_grad = np.dot(H, Theta) + l*X
    Theta_grad = np.dot(X.transpose(), H).transpose() + l*Theta

    # concatenate into 1-d vector
    grad = np.reshape(X_grad, (num_movies*num_features))
    grad = np.concatenate((grad, np.reshape(Theta_grad, (num_users*num_features))))
    return grad 

def normalizeRating(Y, R):
    m, n = Y.shape
    Ymean = np.zeros((m, 1))
    Ynorm = np.zeros((m, n))
    for i in range(m):
        idx = R[i].nonzero()
        Ymean[i] = np.mean(Y[i][idx])
        Ynorm[i][idx] = Y[i][idx] - Ymean[i]
    return Ynorm, Ymean


def checkCostFunction(l):
    # Load Pre-defined data
    subX = np.loadtxt("./subX.txt", dtype=np.float32, delimiter=",")
    subY = np.loadtxt("./subY.txt", dtype=np.float32, delimiter=",")
    subTheta = np.loadtxt("./subTheta.txt", dtype=np.float32, delimiter=",")
    subR = np.loadtxt("./subR.txt", dtype=np.float32, delimiter=",")

    print "before Check", subX.shape, subTheta.shape
    # Merge X and Theta into 1-d array
    num_movies, num_features = subX.shape
    num_users, _ = subTheta.shape
    params = np.reshape(subX, (num_movies*num_features))
    params = np.concatenate((params, np.reshape(subTheta, (num_users*num_features))))
    J = costFunction(params, subY, subR, num_users, num_movies, num_features, 1.5)
    grad = gradientStep(params, subY, subR, num_users, num_movies, num_features, 1.5)
    print J
    tX = np.reshape(grad[0:num_movies*num_features], (num_movies, num_features))
    tTheta = np.reshape(grad[num_movies*num_features:], (num_users, num_features))
    print tX
    print tTheta

# check the implementation of cost function
checkCostFunction(1.5)

# load training data
Y = np.loadtxt("./for_numpy_Y.txt", dtype=np.float32, delimiter=",")
R = np.loadtxt("./for_numpy_R.txt", dtype=np.float32, delimiter=",")
num_movies, num_users = Y.shape
num_features = 10

# add new user and its ratings
my_rating = np.zeros((num_movies, 1))
my_rating[0] = 4
my_rating[97] = 2
my_rating[6] = 3
my_rating[11]= 5;
my_rating[53] = 4;
my_rating[63]= 5;
my_rating[65]= 3;
my_rating[68] = 5;
my_rating[182] = 4;
my_rating[225] = 5;
my_rating[354]= 5;

r = np.zeros((num_movies, 1))
Y = np.c_[my_rating, Y]

r[my_rating.nonzero()] = 1

R = np.c_[r, R]
num_users += 1
lamda = 10

# normalize Y
Ynorm, Ymean = normalizeRating(Y, R)

# initialize parameters
X = np.random.randn(num_movies, num_features)
Theta = np.random.randn(num_users, num_features)
params = np.reshape(X, (num_movies*num_features))
params = np.concatenate((params, np.reshape(Theta, (num_users*num_features))))

# training our data
xopt = fmin_cg(costFunction, params, fprime=gradientStep, 
            args=(Ynorm, R, num_users, num_movies, num_features, lamda), maxiter=100)

train_X = np.reshape(xopt[0:num_movies*num_features], (num_movies, num_features))
train_Theta = np.reshape(xopt[num_movies*num_features:], (num_users, num_features))

# calculate prediction
p = np.dot(train_X, train_Theta.transpose())
p = p[:,0] + Ymean.flatten()

# output prediction
idx = np.argsort(p)[::-1]
for i in range(10):
    print "movie item: ", idx[i], " predict: ", p[idx[i]]

