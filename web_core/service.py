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

USER_INFO_TABLE = 'user_info'

class CoreService:
    """provide service to api-server, abstract away database access
       and collaborative-filtering"""
    def __init__(self):
        self.init = False
        self.con = None
        self.meta = None
        self.token_list = None
        self.max_id = 0

    def start(self):
        try:
            self.con, self.meta = connect('cf_webmovie', 'cf_wmtester', 'webmovie')
        except:
            print "DB-connection fail"
            return False
        # make sure all tables are created
        if USER_INFO_TABLE not in self.meta.tables:
            usr = orm.Table(USER_INFO_TABLE, self.meta,
                            orm.Column('user_id', orm.Integer, primary_key=True),
                            orm.Column('email', orm.String),
                            orm.Column('passphrase', orm.String))
            self.token_list = []
        else:
            result = self.con.execute(orm.sql.text("select max(user_id) from "+USER_INFO_TABLE))
            self.max_id, = result.fetchone()
            self.max_id = 0 if self.max_id is None else self.max_id
            self.token_list = [None for i in range(self.max_id)]

        self.meta.create_all(self.con)
        return True

    def register(self, email, password):
        """Search and compare email, add new user and return UserID"""
        usr = self.meta.tables[USER_INFO_TABLE]
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
        usr = self.meta.tables[USER_INFO_TABLE]
        result = self.con.execute(usr.select().where(usr.c.email == email)).fetchone()
        if result is None:
            return -1, None
        pw = result['passphrase']
        user_id = result['user_id']
        if sha256_crypt.verify(password, pw):
            return user_id, self._generate_token(self.max_id)
        else:
            return -1, None

    def verify_token(self, user_id, token):
        """verify the user_id:token pair"""
        if user_id <= len(self.token_list) and self.token_list[user_id-1] == token:
            return True
        return False

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
