import os
import sys
import getopt
import numpy as np
import collabor_filtering as cf
import matplotlib.pyplot as plt

def main(argv):
    """perform cross validation"""
    lamda_v = [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100]
    ml_dir = None
    try:
        opts, args = getopt.getopt(argv, "hi:", ["input="])
    except getopt.GetoptError:
        _usage()
    for opt, arg in opts:
        if opt == "-h":
            _usage()
        elif opt in ("-i", "--input"):
            ml_dir = arg 
    if ml_dir is None:
        _usage()

    os.chdir(ml_dir)

    num_movies, num_users = _load_info()

    for i in range(len(lamda_v)):
        subplt = plt.subplot(3, 3, i+1)
        subplt.set_ylabel("cost", fontsize=8)
        subplt.set_xlabel("feature", fontsize=8)
        _cross_valid_feature(1, num_movies,
                             num_users, lamda_v[i], subplt)
        subplt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                      ncol=2, mode="expand", borderaxespad=0)
    plt.show()

def _usage():
    print __file__, "-i <movielen data directory>"
    sys.exit(2)

def _load_info():
    f_info = open("u.info")
    for line in f_info:
        info = line.strip('\n').split(" ")
        if info[1] == "users":
            num_users = int(info[0])
        elif info[1] == "items":
            num_movies = int(info[0])
        elif info[1] == "ratings":
            num_ratings = int(info[0])
    f_info.close()
    return num_movies, num_users

def _load_data(fold_id, ext, ratings, valid_ratings):
    f_name = "u" + str(fold_id) + ext
    f_data = open(f_name)
    count = 0
    for line in f_data:
        items = line.strip('\n').split('\t')
        user_id = int(items[0])
        movie_id = int(items[1])
        rate = int(items[2])
        ratings[movie_id-1][user_id-1] = rate
        valid_ratings[movie_id-1][user_id-1] = 1
        count += 1
    f_data.close()
    return count

def _cross_valid_fold(fold_id, num_movies, num_users, num_features, lamda):
    """k-th-fold cross validation"""
    ratings = np.zeros(shape=(num_movies, num_users))
    valid_ratings = np.zeros(shape=(num_movies, num_users))
    train_data_num = _load_data(fold_id, ".base", ratings, valid_ratings)

    mf = cf.MFactor(ratings, valid_ratings)
    cost = mf.training(num_features, lamda)
    cost = cost / train_data_num

    # calculation cross-validation loss
    cross_ratings = np.zeros(shape=(num_movies, num_users))
    cross_valid_ratings = np.zeros(shape=(num_movies, num_users))
    cv_data_num = _load_data(fold_id, ".test",
                             cross_ratings, cross_valid_ratings)

    cost_cv = mf.loss(cross_ratings, cross_valid_ratings, lamda)
    cost_cv = cost_cv / cv_data_num
    print num_features, fold_id, "train_cost:", cost, " cross_cost:", cost_cv
    return cost, cost_cv

def _cross_valid_feature(max_fold, num_movies, num_users, lamda, subplt):
    """5-fold cross validation on num_feature(1~30)"""
    loss_train_vector = [.0]*31
    loss_cross_vector = [.0]*31
    cost_train_per_fold = [.0]*max_fold
    cost_cross_per_fold = [.0]*max_fold
    for i in range(1,  31, 1):
        for k in range(1, max_fold + 1, 1):
            cost_train_per_fold[k-1], cost_cross_per_fold[k-1] = (
                _cross_valid_fold(k, num_movies, num_users,
                                  i, lamda))
        loss_train_vector[i] = np.mean(cost_train_per_fold)
        loss_cross_vector[i] = np.mean(cost_cross_per_fold)

    # draw the Loss v.s num_feature graph
    subplt.plot(loss_train_vector, "r")
    subplt.plot(loss_cross_vector, "b")
    v1 = np.array(loss_cross_vector)
    v2 = np.array(loss_train_vector)
    v3 = v1 + v2
    sel_feature = np.argmin(v3[1:]) + 1
    subplt.plot(v3, "g", label="lambda="+str(lamda))
    plt.axis([1, 30, 0, 1.2*max(v3)])
    return sel_feature
 
if __name__ == "__main__":
    main(sys.argv[1:])
