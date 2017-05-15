import numpy as np
from scipy.optimize import fmin_cg

class MFactor:
    """ A matrix factorization - collaborative filtering algorthm """
    def __init__(self, ratings, valid_ratings):
        self.features = None
        self.coeff = None
        self.labels_mean = None
        self.ratings = ratings
        self.valid_ratings = valid_ratings

    def training(self, num_features, lamda):
        num_movies, num_users = self.ratings.shape
        #labels_norm, self.labels_mean = _normalize_rating(self.ratings,
        #                                                  self.valid_ratings)

        # initialize parameters
        X = np.random.randn(num_movies, num_features)
        Theta = np.random.randn(num_users, num_features)
        params = np.reshape(X, (num_movies*num_features))
        params = np.concatenate((params, np.reshape(Theta,
                                (num_users*num_features))))

        # training our data
        xopt, fopt, _, _, _ = fmin_cg(
            _cost_function, params, fprime=_gradient_step,
            args=(self.ratings, self.valid_ratings, num_users,
                  num_movies, num_features, lamda),
            maxiter=100, full_output=True)

        self.features = np.reshape(xopt[0:num_movies*num_features],
                             (num_movies, num_features))
        self.coeff = np.reshape(xopt[num_movies*num_features:],
                             (num_users, num_features))
        return fopt

    def predict(self, userID):
        p = np.dot(self.features, self.coeff.transpose())
        p = p[:,userID] + self.labels_mean.flatten()
        return p

    def loss(self, ratings, valid_ratings, lamda):
        """Calculate the loss of the input data base on the trained
           features and coefficient.
        """
        num_movies, num_users = ratings.shape
        _, num_features = self.features.shape
        # caculate normalized rating base on the rating mean in training
        #ratings_norm = np.zeros((num_movies, num_users))
        #for i in range(num_movies):
        #    idx, = valid_ratings[i].nonzero()
        #    if len(idx) != 0:
        #        ratings_norm[i][idx] = ratings[i][idx] - self.labels_mean[i]

        # concatenate into 1d vector
        params = np.reshape(self.features, (num_movies*num_features))
        params = np.concatenate((params, np.reshape(self.coeff, 
                                                    (num_users*num_features))))
        return _cost_function(params, ratings, valid_ratings,
                              num_users, num_movies, num_features, lamda)

def main():
    # check the implementation of cost function
    _check_costfunction(1.5)

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

    mf = MFactor(Y, R)

    loss = mf.training(10, 10)

    prediction = mf.predict(0)

    # output prediction
    idx = np.argsort(prediction)[::-1]
    for i in range(10):
        print "movie item: ", idx[i], " predict: ", prediction[idx[i]]


def _cost_function(params, Y, R, num_users, num_movies, num_features, lamda):
    # reshape 1d params into matrices: X, Theta
    X = np.reshape(params[0:num_movies*num_features],
                   (num_movies, num_features))
    Theta = np.reshape(params[num_movies*num_features:],
                       (num_users, num_features))

    # calculate Cost
    H = (np.dot(X,Theta.transpose()) - Y) * R
    J = (sum(sum(H ** 2))/2
        + (lamda/2)*sum(sum(Theta ** 2))    # regularization term
        + (lamda/2)*sum(sum(X **2)))        # regularization term
    return J

def _gradient_step(params, Y, R, num_users, num_movies, num_features, lamda):
    # reshape 1d params into matrices: X, Theta
    X = np.reshape(params[0:num_movies*num_features],
                   (num_movies, num_features))
    Theta = np.reshape(params[num_movies*num_features:],
                   (num_users, num_features))

    # calculate Gradient
    H = (np.dot(X,Theta.transpose()) - Y) * R
    X_grad = np.dot(H, Theta) + lamda*X
    Theta_grad = np.dot(X.transpose(), H).transpose() + lamda*Theta

    # concatenate into 1d vector
    grad = np.reshape(X_grad, (num_movies*num_features))
    grad = np.concatenate((grad, np.reshape(Theta_grad,
                          (num_users*num_features))))
    return grad 

def _normalize_rating(Y, R):
    m, n = Y.shape
    y_mean = np.zeros((m, 1))
    y_norm = np.zeros((m, n))
    for i in range(m):
        idx, = R[i].nonzero()
        y_mean[i] = np.mean(Y[i][idx]) if len(idx) != 0 else 0
        y_norm[i][idx] = Y[i][idx] - y_mean[i]
    return y_norm, y_mean

def _check_costfunction(l):
    # Load Pre-defined data
    subX = np.loadtxt("./subX.txt", dtype=np.float32, delimiter=",")
    subY = np.loadtxt("./subY.txt", dtype=np.float32, delimiter=",")
    subTheta = np.loadtxt("./subTheta.txt",
            dtype=np.float32, delimiter=",")
    subR = np.loadtxt("./subR.txt", dtype=np.float32, delimiter=",")

    # Merge X and Theta into 1-d array
    num_movies, num_features = subX.shape
    num_users, _ = subTheta.shape
    params = np.reshape(subX, (num_movies*num_features))
    params = np.concatenate((params, np.reshape(subTheta,
        (num_users*num_features))))
    J = _cost_function(params, subY, subR, num_users,
            num_movies, num_features, 1.5)
    grad = _gradient_step(params, subY, subR, num_users,
            num_movies, num_features, 1.5)
    tX = np.reshape(grad[0:num_movies*num_features],
            (num_movies, num_features))
    tTheta = np.reshape(grad[num_movies*num_features:],
            (num_users, num_features))
    print J
    print tX
    print tTheta

if __name__ == "__main__":
    main()
