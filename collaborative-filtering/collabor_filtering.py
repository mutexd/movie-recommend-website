import numpy as np

def GradientStep(X, Y, R, Theta, l):
    H = (np.dot(X,Theta.transpose()) - Y) * R
    J = sum(sum(H ** 2)) / 2 + (l/2)*sum(sum(Theta ** 2)) + (l/2)*sum(sum(X **2))
    X_grad = np.dot(H, Theta) + l*X
    Theta_grad = np.dot(X.transpose(), H).transpose() + l*Theta

    return J, X_grad, Theta_grad

def GradientDescent(X, Y, R, Theta, alpha, l, num_iters):
    m, _ = Y.shape
    for i in range(num_iters):
        J, X_grad, Theta_grad = GradientStep(X, Y, R, Theta, l)
        
        X = X - alpha*X_grad
        Theta = Theta - alpha*Theta_grad
        print "cost: ", J
    return X, Theta

def checkCostFunction(l):
    # Load Pre-defined data
    subX = np.loadtxt("./subX.txt", dtype=np.float32, delimiter=",")
    subY = np.loadtxt("./subY.txt", dtype=np.float32, delimiter=",")
    subTheta = np.loadtxt("./subTheta.txt", dtype=np.float32, delimiter=",")
    subR = np.loadtxt("./subR.txt", dtype=np.float32, delimiter=",")

    J, X_grad, Theta_grad = GradientStep(subX, subY, subR, subTheta, 1.5)
    print J
    print X_grad
    print Theta_grad

# check the implementation of cost function
checkCostFunction(1.5)

Y = np.loadtxt("./for_numpy_Y.txt", dtype=np.float32, delimiter=",")
R = np.loadtxt("./for_numpy_R.txt", dtype=np.float32, delimiter=",")
num_movies, num_users = Y.shape
num_features = 10

my_rating = np.zeros((num_movies, 1))
my_rating[0] = 4
my_rating[98] = 2
my_rating[7] = 3
my_rating[12]= 5;
my_rating[54] = 4;
my_rating[64]= 5;
my_rating[66]= 3;
my_rating[69] = 5;
my_rating[183] = 4;
my_rating[226] = 5;
my_rating[355]= 5;

r = np.zeros((num_movies, 1))
Y = np.c_[my_rating, Y]

for i in range(num_movies):
    r[i] = 1 if my_rating[i] != 0 else 0

R = np.c_[r, R]

X = np.random.rand(num_movies, num_features)
Theta = np.random.rand(num_users+1, num_features)
print X.shape
print Theta.shape

train_X, train_Theta = GradientDescent(X, Y, R, Theta, 0.001, 3, 300)

p = np.dot(train_X, train_Theta.transpose())
p = p[:,0]
idx = np.argsort(p)[::-1]
for i in range(10):
    print "movie item: ", idx[i], " predict: ", p[idx[i]]
