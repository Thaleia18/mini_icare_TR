import sqlite3


class UniversityDatabase:
    def __init__(self, database_name):
        self.database_name = database_name
        try:
          conn = sqlite3.connect(self.database_name)
          print("Database created: ",database_name)
        except:
          print("Database not formed.")
      
      
    def create_tables(self):
        sql_statements = [
            "DROP TABLE IF EXISTS universities;",
            """
            CREATE TABLE IF NOT EXISTS universities (
                univ_name TEXT PRIMARY KEY,
                home_url TEXT NOT NULL,
                undergrad_url TEXT,
                search_url TEXT,
                requirements_url TEXT,
                scolarchips_url TEXT,
                deadlines_url TEXT
            );
            """,
            "DROP TABLE IF EXISTS deadlines;",
            """
            CREATE TABLE IF NOT EXISTS deadlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                univ_name TEXT NOT NULL,
                entry_year TEXT NOT NULL,
                date TEXT NOT NULL,
                action TEXT NOT NULL,
                FOREIGN KEY (univ_name) REFERENCES universities(univ_name)
            );
            """,
            "DROP TABLE IF EXISTS courses;",
                        """
                        CREATE TABLE IF NOT EXISTS courses (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            univ_name TEXT NOT NULL,
                            course_name TEXT NOT NULL,
                            course_url TEXT NOT NULL,
                            degree TEXT NOT NULL,
                            hons TEXT, 
                            offer_level TEXT,
                            ucas_code TEXT,
                            course_length TEXT,
                            start_date TEXT,
                            location TEXT,
                            deadline_apply,
                            FOREIGN KEY (univ_name) REFERENCES universities(univ_name)
                        );
                        """            ]

        try:
            with sqlite3.connect(self.database_name) as conn:
                cursor = conn.cursor()
                for stmt in sql_statements:
                    cursor.execute(stmt)
                conn.commit()
                print("Tables created successfully.")
        except sqlite3.OperationalError as e:
            print("Failed to create tables:", e)
      
def add_university(database_name, values):
    try:
        sqliteConnection = sqlite3.connect(database_name)
        #print("Connected to SQLite")
        sql = ''' INSERT INTO universities(univ_name, home_url, undergrad_url, 
                    search_url, requirements_url, scolarchips_url, deadlines_url)
                  VALUES(?,?,?,?,?,?,?) '''      
        # Create  a cursor
        cur = sqliteConnection.cursor()
        # execute the INSERT statement
        cur.execute(sql, values)
        # commit the changes
        sqliteConnection.commit()
        print(f'Created a university record with the id {values[0]}')
        sqliteConnection.close()
       # return cur.lastrowid  
    except sqlite3.Error as error:
            print("Failed to connect with sqlite3 database", error)
            
def add_deadlines(database_name, values):
    try:
        sqliteConnection = sqlite3.connect(database_name)
        #print("Connected to SQLite")

        sql = '''INSERT INTO deadlines (univ_name, entry_year, date, action)
                 VALUES (?, ?, ?, ?)'''
        cur = sqliteConnection.cursor()
        cur.execute(sql, values)
        sqliteConnection.commit()
        cur.close()
        sqliteConnection.close()
  #      print("Deadline added successfully")     
    except sqlite3.Error as error:
        quit#print("Failed to insert data into SQLite table", error) 

def add_courses(database_name, values):
    try:
        sqliteConnection = sqlite3.connect(database_name)
        #print("Connected to SQLite")

        sql = '''INSERT INTO courses (univ_name, course_name, degree, hons,
                    course_url, offer_level, ucas_code, course_length, start_date, location, deadline_apply)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        cur = sqliteConnection.cursor()
        cur.execute(sql, values)
        sqliteConnection.commit()
        cur.close()
        sqliteConnection.close()
    #    print("Deadline added successfully")       
    except sqlite3.Error as error:
        quit
        #print("Failed to insert data into SQLite table", error)         
    
    
if __name__ == "__main__":
    mydb = UniversityDatabase('univ_database.db')
    mydb.create_tables()