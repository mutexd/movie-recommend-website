import sqlalchemy as orm
import numpy as np
from passlib.hash import sha256_crypt
import random, string
import time
import collaborative_filtering.collabor_filtering as cf

def main():
    """test"""
    svc = CoreService()
    if svc.start() == False:
        return
    rval = svc.register("joshd1986@gmail.com", "123456")
    if rval >= 0:
        print "Registeration success"
    else:
        print "Already used email, fail"
        return

    rval = svc.auth("joshd1986@gmail.com", "123456")
    if rval >= 0:
        print "Verified joshd1986@gmail.com"
    else:
        print "Verified error"

    rval = svc.auth("joshd1986@gmail.com", "1236")
    if rval >= 0:
        print "Verified joshd1986@gmail.com"
    else:
        print "Verified error"

    rval = svc.auth("joshd@gmail.com", "1236")
    if rval >= 0:
        print "Verified joshd1986@gmail.com"
    else:
        print "Verified error"

### Constants

_USER_INFO_TABLE = 'user_info'
_MOVIE_INFO_TABLE = 'movie_info'
_RATING_INFO_TABLE = 'rating_info'

_USER_ID_KEY = 'user_id'
_EMAIL_KEY = 'email'
_PW_KEY = 'passphrase'
_MOVIE_ID_KEY = 'movie_id'
_TITLE_KEY = 'title'
_DATE_KEY = 'date'
_IMDB_URL_KEY = 'imdb_url'
_THUMB_URL_KEY = 'thumb_url'
_DURATION_KEY = 'duration'
_PRESENT_TITLE_KEY = 'present_title'
_TIMESTAMP_KEY = 'timestamp'
_RATING_KEY = 'rating'

class CoreService:
    """provide service to api-server, abstract away database access
       and collaborative-filtering"""
    def __init__(self):
        self.init = False
        self.con = None
        self.meta = None
        self.token_list = None
        self.max_id = 0

        self.num_movies = 0
        self.num_inactive_users = 0 # users from movielen data
        self.num_users = 0
        self.ratings = None
        self.valid_ratings = None

    def start(self, movie_len_dir):
        print movie_len_dir
        try:
            self.con, self.meta = connect('cf_webmovie', 'cf_wmtester', 'webmovie')
        except:
            print "DB-connection fail"
            return False

        ### make sure all db-tables are created
        if _USER_INFO_TABLE not in self.meta.tables:
            print "user_info table created"
            usr = orm.Table(_USER_INFO_TABLE, self.meta,
                            orm.Column(_USER_ID_KEY, orm.Integer, primary_key=True),
                            orm.Column(_EMAIL_KEY, orm.String),
                            orm.Column(_PW_KEY, orm.String))
            self.token_list = []
        else:
            result = self.con.execute(orm.sql.text("select max(user_id) from "+_USER_INFO_TABLE))
            self.max_id, = result.fetchone()
            self.max_id = 0 if self.max_id is None else self.max_id
            self.token_list = [None for i in range(self.max_id)]

        to_create_movie_table = False
        if _MOVIE_INFO_TABLE not in self.meta.tables:
            print "movie_info table created"
            to_create_movie_table = True
            movie_table = orm.Table(_MOVIE_INFO_TABLE, self.meta,
                                    orm.Column(_MOVIE_ID_KEY, orm.Integer, primary_key=True),
                                    orm.Column(_TITLE_KEY, orm.String),
                                    orm.Column(_DATE_KEY, orm.String),
                                    orm.Column(_IMDB_URL_KEY, orm.String),
                                    orm.Column(_THUMB_URL_KEY, orm.String),
                                    orm.Column(_DURATION_KEY, orm.String),
                                    orm.Column(_PRESENT_TITLE_KEY, orm.String))

        if _RATING_INFO_TABLE not in self.meta.tables:
            print "rating_info table created"
            rating_table = orm.Table(_RATING_INFO_TABLE, self.meta,
                                     orm.Column(_USER_ID_KEY, orm.Integer),
                                     orm.Column(_MOVIE_ID_KEY, orm.Integer),
                                     orm.Column(_RATING_KEY, orm.Integer),
                                     orm.Column(_TIMESTAMP_KEY, orm.Integer))

        self.meta.create_all(self.con)
        if to_create_movie_table == True:
            self._load_movie_table(movie_len_dir + "/u.item")

        ### initialize matrix (rating, rating_valid)
        self.num_movies, self.num_inactive_users = load_movieLen_info(movie_len_dir + "/u.info")
        # allocate more rows for future user
        self.num_users = (self.num_inactive_users + self.max_id) * 2
        self.ratings = np.zeros(shape=(self.num_movies, self.num_users))
        self.valid_ratings = np.zeros(shape=(self.num_movies, self.num_users))
        ## load from movieLen data
        data_num = load_movieLen_data(movie_len_dir + "/u.data", self.ratings, self.valid_ratings)
        print "load ", data_num, "of rating data from movieLen"
        ## load from database data
        rating_tbl = self.meta.tables[_RATING_INFO_TABLE]
        result = self.con.execute(rating_tbl.select())
        print "max_id:", self.max_id
        for row in result:
            print "user %d rate %d for movie_id(%d)" %(row.user_id, row.rating, row.movie_id)
            self.ratings[row.movie_id-1][row.user_id+self.num_inactive_users-1] = row.rating
            self.valid_ratings[row.movie_id-1][(row.user_id
                                               +self.num_inactive_users-1)] = 1
        ### let's kick-off MFactor training here
        #self.training()
        #print "Initial training complete"
        return True

    def register(self, email, password):
        """Search and compare email, add new user and return UserID"""
        usr = self.meta.tables[_USER_INFO_TABLE]
        result = self.con.execute(usr.select().where(usr.c.email == email))
        if result.rowcount == 0: # not found, add this new user
            self.max_id += 1
            # salt+hash
            pw = sha256_crypt.encrypt(password)
            self.con.execute(usr.insert().values(user_id=self.max_id,
                                                 email=email,
                                                 passphrase=pw))
            return self.max_id, self._generate_token(self.max_id)
        else: # conflict, cannot add this user
            return -1, None

    def auth(self, email, password):
        """Search and verify passphrase, return corresponding UserID"""
        usr = self.meta.tables[_USER_INFO_TABLE]
        result = self.con.execute(usr.select().where(usr.c.email == email)).fetchone()
        if result is None:
            return -1, None
        pw = result[_PW_KEY]
        user_id = result[_USER_ID_KEY]
        if sha256_crypt.verify(password, pw):
            return user_id, self._generate_token(self.max_id)
        else:
            return -1, None

    def verify_token(self, user_id, token):
        """verify the user_id:token pair"""
        if user_id <= len(self.token_list) and self.token_list[user_id-1] == token:
            return True
        return False

    def avg_ranking(self, begin, end):
        """return list of movie ranking from start to end"""
        ## calculate avg_ranking from ratings
        m, n = self.ratings.shape
        ratings_mean = np.zeros((m, 1))
        for i in range(m):
            idx, = self.valid_ratings[i].nonzero()
            ratings_mean[i] = np.mean(self.ratings[i][idx]) if len(idx) != 0 else 0
        avg_idx = np.argsort(ratings_mean, axis=0)[::-1]
        avg_idx = avg_idx + 1 # from index to movie_id
        avg_idx = avg_idx.flatten().tolist()
        return self._get_movie_list(avg_idx, begin, end)

    def _get_movie_list(self, id_list, begin, end):
        movie = self.meta.tables[_MOVIE_INFO_TABLE]
        result = self.con.execute(movie.select().where(movie.c.movie_id.in_(id_list[begin:end])))
        data = [None] * len(id_list[begin:end])
        for row in result:
            ## result from SQL is not sorted, sort it here
            for idx in range(begin, end, 1):
                if row.movie_id == id_list[idx]:
                    data[idx-begin] = ({_MOVIE_ID_KEY: row.movie_id,
                                        _TITLE_KEY: row.title,
                                        _THUMB_URL_KEY: row.thumb_url})
                    break
        return data

    def add_rating(self, user_id, movie_id, rating):
        """add rating into database and rating_matrix"""
        ### need sanity checking here
        if movie_id > self.num_movies or movie_id < 1 or rating > 5 or rating < 1:
            print "invalid input"
            return False
        ### when to kick-off MFactor training?
        rating_tbl = self.meta.tables[_RATING_INFO_TABLE]
        self.con.execute(rating_tbl.insert().values(user_id=user_id,
                                                movie_id=movie_id,
                                                rating=rating,
                                                timestamp=int(time.time())))
        if user_id > self.num_users:
            new_usr_rating = np.zero((self.num_movies, 1))
            self.ratings = np.c_[self.ratings, new_usr_rating]
            self.num_users += 1
        self.ratings[movie_id-1][user_id+self.num_inactive_users-1] = rating
        self.valid_ratings[movie_id-1][user_id+self.num_inactive_users-1] = 1
        print "user:", user_id, "rate ",rating,"on movie_id=",movie_id
        print self.ratings[movie_id-1][user_id+self.num_inactive_users-1]
        return True

    def training(self):
        self.mf = cf.MFactor(self.ratings, self.valid_ratings)
        self.mf.training(10, 1)

    def get_prediction(user_id, begin, end):
        prediction = self.mf.predict(user_id + self.num_inactive_users - 1)
        _get_movie_list(prediction, begin, end)

    def _generate_token(self, user_id):
        """generate token and save it to user_id:token list"""
        ### TODO - provide expire_time and refresh_token

        token = ''.join(random.choice(string.ascii_letters + string.digits) for n in xrange(128))
        ### enlarge token_list if not enough
        if user_id > len(self.token_list):
            for i in range(user_id - len(self.token_list)):
                self.token_list.append(None)
        self.token_list[user_id-1] = token
        return token

    def _load_movie_table(self, filename):
        """update movie table from movieLen data"""
        f_info = open(filename)
        data = []
        movie = self.meta.tables[_MOVIE_INFO_TABLE]
        for line in f_info:
            items = line.strip('\n').split('|')
            data.append({_MOVIE_ID_KEY: items[0],
                         _TITLE_KEY: items[1].decode('iso-8859-1').encode('utf8'),
                         _DATE_KEY: items[2],
                         _IMDB_URL_KEY: items[4],
                         _THUMB_URL_KEY: 'oops.jpeg',
                         _DURATION_KEY: '0 min',
                         _PRESENT_TITLE_KEY: 'unknown'})
        self.con.execute(movie.insert().values(data))
        f_info.close()


def connect(user, password, db, host='localhost', port=5432):
    """Returns a connetion and meta-data object"""

    # postgresql://federer:grandestslam@localhost:5432/tennis
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)

    # connection object
    con = orm.create_engine(url, client_encoding='utf8')

    # bind connection object to MetaData()
    meta = orm.MetaData(bind=con, reflect=True)

    return con, meta

def load_movieLen_info(filename):
    f_info = open(filename)
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

def load_movieLen_data(filename, ratings, valid_ratings):
    f_data = open(filename)
    count = 0
    print ratings.shape
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


if __name__ == "__main__":
    main()
