import os
import psycopg2

conn = psycopg2.connect(
        host="localhost",
        database="flask_db",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'])

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
cur.execute('DROP TABLE IF EXISTS users;')
cur.execute('CREATE TABLE users (id serial PRIMARY KEY,'
                                 'username varchar (255) NOT NULL,'
                                 'password varchar (255) NOT NULL,'
                                 'date_added date DEFAULT CURRENT_TIMESTAMP);'
                                 )
cur.execute('DROP TABLE IF EXISTS books;')
cur.execute('CREATE TABLE images (id serial PRIMARY KEY,'
                                 'title varchar (255) NOT NULL,'
                                 'path varchar (255) NOT NULL,'
                                 'profil_id integer NOT NULL,'
                                 'date_added date DEFAULT CURRENT_TIMESTAMP);'
                                 )

# Insert data into the table

cur.execute('INSERT INTO images (title, path, profil_id)'
            'VALUES (%s, %s, %s)',
            ('Sammy Image',
             'https://www.arthurguerin.com/assets/www.png',
             1)
            )

cur.execute('CREATE EXTENSION pgcrypto;')
cur.execute("INSERT INTO users (username, password) VALUES ('test@test.com',crypt('test', gen_salt('bf')));")

conn.commit()

cur.close()
conn.close()