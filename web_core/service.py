import sqlalchemy as orm
from passlib.hash import sha256_crypt

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
        self.meta.create_all(self.con)
        return True

    def register(self, email, password):
        """Search and compare email, add new user and return UserID"""
        usr = self.meta.tables[USER_INFO_TABLE]
        result = self.con.execute(usr.select().where(usr.c.email == email))
        if result.rowcount == 0: # not found, add this new user
            result = self.con.execute(orm.sql.text("select max(user_id) from "+USER_INFO_TABLE))
            max_id, = result.fetchone()
            max_id = 0 if max_id is None else max_id
            # salt+hash
            pw = sha256_crypt.encrypt(password)
            self.con.execute(usr.insert().values(user_id=max_id + 1,
                                                 email=email,
                                                 passphrase=pw))
            return max_id + 1
        else: # conflict, cannot add this user
            return -1

    def auth(self, email, password):
        """Search and verify passphrase, return corresponding UserID"""
        usr = self.meta.tables[USER_INFO_TABLE]
        result = self.con.execute(usr.select().where(usr.c.email == email)).fetchone()
        if result is None:
            return -1
        pw = result['passphrase']
        if sha256_crypt.verify(password, pw):
            return result['user_id']
        else:
            return -1
        
    #def add_rating(user_id, movie_id, rating):

    #def get_prediction(user_id, r):

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
