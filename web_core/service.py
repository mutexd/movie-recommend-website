import sqlalchemy as orm
from passlib.hash import sha256_crypt
import random, string

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

_USER_INFO_TABLE = 'user_info'
_MOVIE_INFO_TABLE = 'movie_info'
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

class CoreService:
    """provide service to api-server, abstract away database access
       and collaborative-filtering"""
    def __init__(self):
        self.init = False
        self.con = None
        self.meta = None
        self.token_list = None
        self.max_id = 0

    def start(self, movie_info_filename):
        print movie_info_filename
        try:
            self.con, self.meta = connect('cf_webmovie', 'cf_wmtester', 'webmovie')
        except:
            print "DB-connection fail"
            return False
        # make sure all tables are created
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

        to_create_table = False
        if _MOVIE_INFO_TABLE not in self.meta.tables:
            print "movie_info table created"
            movie_table = orm.Table(_MOVIE_INFO_TABLE, self.meta,
                                    orm.Column(_MOVIE_ID_KEY, orm.Integer, primary_key=True),
                                    orm.Column(_TITLE_KEY, orm.String),
                                    orm.Column(_DATE_KEY, orm.String),
                                    orm.Column(_IMDB_URL_KEY, orm.String),
                                    orm.Column(_THUMB_URL_KEY, orm.String),
                                    orm.Column(_DURATION_KEY, orm.String),
                                    orm.Column(_PRESENT_TITLE_KEY, orm.String))
            to_create_table = True
        self.meta.create_all(self.con)
        if to_create_table == True:
            self._load_movie_table(movie_info_filename)
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

    def avg_ranking(self, start, end):
        """return list of movie ranking from start to end"""
        movie = self.meta.tables[_MOVIE_INFO_TABLE]
        result = self.con.execute(movie.select().where(movie.c.movie_id.in_(range(start, end))))
        data = []
        for row in result:
            data.append({_MOVIE_ID_KEY: row.movie_id,
                         _TITLE_KEY: row.title,
                         _THUMB_URL_KEY: row.thumb_url})
        return data
    #def add_rating(user_id, movie_id, rating):

    #def get_prediction(user_id, r):

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
        """load movie table"""
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

if __name__ == "__main__":
    main()
