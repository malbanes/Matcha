import os
import psycopg2

DBFILES = [
        "flask_db_public_users.sql",
        "flask_db_public_accountcontrol.sql",
        "flask_db_public_images.sql",
        "flask_db_public_Interest.sql",
        "flask_db_public_likes.sql",
        "flask_db_public_messages.sql",
        "flask_db_public_notifications.sql",
        "flask_db_public_search.sql",
        "flask_db_public_location.sql",
        "flask_db_public_visites.sql",
        "flask_db_public_match.sql",
        "flask_db_public_profil.sql",
        "flask_db_public_ProfilInterest.sql"
]

def executeScriptsFromFile(c, conn):
        # Open and read the file as a single buffer
        for file in DBFILES:
                fd = open("../gen_db/" + file, 'r')
                sqlFile = fd.read()
                fd.close()

                # all SQL commands (split on ';')
                sqlCommands = sqlFile.split(';')

                # Execute every command from the input file
                for command in sqlCommands:
                    # This will skip and report errors
                    # For example, if the tables do not yet exist, this will skip over
                    # the DROP TABLE commands
                        if command:
                                command = command + " ;"
                                print(command)
                                try:
                                        c.execute(command)
                                except:
                                        print("Command skipped: ", command)
                                conn.commit()

def main():
        conn = psycopg2.connect(
                host="localhost",
                database="flask_db",
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'))

        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Execute a command: this creates a new table
        cur.execute('DROP TABLE IF EXISTS accountcontrol;')
        cur.execute('DROP TABLE IF EXISTS images;')
        cur.execute('DROP TABLE IF EXISTS likes;')
        cur.execute('DROP TABLE IF EXISTS match;')
        cur.execute('DROP TABLE IF EXISTS messages;')
        cur.execute('DROP TABLE IF EXISTS notifications;')
        cur.execute('DROP TABLE IF EXISTS \"ProfilInterest\";')
        cur.execute('DROP TABLE IF EXISTS \"Interest\";')
        cur.execute('DROP TABLE IF EXISTS search;')
        cur.execute('DROP TABLE IF EXISTS visites;')
        cur.execute('DROP TABLE IF EXISTS profil;')
        cur.execute('DROP TABLE IF EXISTS location;')
        cur.execute('DROP TABLE IF EXISTS users;')
        conn.commit()
        try:
                cur.execute('CREATE EXTENSION pgcrypto;')
        except:
                print("pgcrypto already exists")
        conn.commit()
        executeScriptsFromFile(cur, conn)
        cur.execute('GRANT all privileges ON TABLE users to sammy;')
        cur.execute('GRANT all privileges ON TABLE accountcontrol to sammy;')
        cur.execute('GRANT all privileges ON TABLE images to sammy;')
        cur.execute('GRANT all privileges ON TABLE \"Interest\" to sammy;')
        cur.execute('GRANT all privileges ON TABLE likes to sammy;')
        cur.execute('GRANT all privileges ON TABLE location to sammy;')
        cur.execute('GRANT all privileges ON TABLE match to sammy;')
        cur.execute('GRANT all privileges ON TABLE messages to sammy;')
        cur.execute('GRANT all privileges ON TABLE notifications to sammy;')
        cur.execute('GRANT all privileges ON TABLE \"ProfilInterest\" to sammy;')
        cur.execute('GRANT all privileges ON TABLE search to sammy;')
        cur.execute('GRANT all privileges ON TABLE visites to sammy;')
        cur.execute('GRANT all privileges ON TABLE profil to sammy;')
        
        cur.execute('GRANT USAGE, SELECT ON SEQUENCE accountcontrol_id_seq TO sammy;')
        cur.execute('GRANT USAGE, SELECT ON SEQUENCE images_id_seq TO sammy;')
        cur.execute('GRANT USAGE, SELECT ON SEQUENCE \"Interest_id_seq\" TO sammy;')
        cur.execute('GRANT USAGE, SELECT ON SEQUENCE likes_id_seq TO sammy;')
        cur.execute('GRANT USAGE, SELECT ON SEQUENCE location_id_seq TO sammy;')
        cur.execute('GRANT USAGE, SELECT ON SEQUENCE match_id_seq TO sammy;')
        cur.execute('GRANT USAGE, SELECT ON SEQUENCE messages_id_seq TO sammy;')
        cur.execute('GRANT USAGE, SELECT ON SEQUENCE notifications_id_seq TO sammy;')
        cur.execute('GRANT USAGE, SELECT ON SEQUENCE profil_id_seq TO sammy;')
        cur.execute('GRANT USAGE, SELECT ON SEQUENCE \"ProfilInterest_id_seq\" TO sammy;')
        cur.execute('GRANT USAGE, SELECT ON SEQUENCE search_id_seq TO sammy;')
        cur.execute('GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO sammy;')
        cur.execute('GRANT USAGE, SELECT ON SEQUENCE visites_id_seq TO sammy;')
        #cur.execute("SELECT setval('notifications_pkey', (SELECT MAX(notifications_pkey) FROM notifications)+1);")
        #cur.execute("SELECT setval('accountcontrol_pkey', (SELECT MAX(accountcontrol_pkey) FROM accountcontrol)+1);")
        #cur.execute("SELECT setval('users_pkey', (SELECT MAX(users_pkey) FROM users)+1);")
        #cur.execute("SELECT setval('images_pkey', (SELECT MAX(images_pkey) FROM images)+1);")
        #cur.execute("SELECT setval('Interest_pkey', (SELECT MAX(Interest_pkey) FROM \"Interest\")+1);")
        #cur.execute("SELECT setval('likes_pkey', (SELECT MAX(likes_pkey) FROM likes)+1);")
        #cur.execute("SELECT setval('location_pkey', (SELECT MAX(location_pkey) FROM location)+1);")
        #cur.execute("SELECT setval('match_pkey', (SELECT MAX(match_pkey) FROM match)+1);")
        #cur.execute("SELECT setval('messages_pkey', (SELECT MAX(messages_pkey) FROM messages)+1);")
        #cur.execute("SELECT setval('ProfilInterest_pkey', (SELECT MAX(ProfilInterest_pkey) FROM \"ProfilInterest\")+1);")
        #cur.execute("SELECT setval('search_pkey', (SELECT MAX(search_pkey) FROM search)+1);")
        #cur.execute("SELECT setval('visites_pkey', (SELECT MAX(visites_pkey) FROM visites)+1);")
        #cur.execute("SELECT setval('profil_pkey', (SELECT MAX(profil_pkey) FROM profil)+1);")
        
        cur.execute("SELECT setval('notifications_id_seq', (SELECT MAX(id) FROM notifications)+1);")
        cur.execute("SELECT setval('accountcontrol_id_seq', (SELECT MAX(id) FROM accountcontrol)+1);")
        cur.execute("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users)+1);")
        cur.execute("SELECT setval('images_id_seq', (SELECT MAX(id) FROM images)+1);")
        cur.execute("SELECT setval('\"Interest_id_seq\"', (SELECT MAX(id) FROM \"Interest\")+1);")
        cur.execute("SELECT setval('likes_id_seq', (SELECT MAX(id) FROM likes)+1);")
        cur.execute("SELECT setval('location_id_seq', (SELECT MAX(id) FROM location)+1);")
        cur.execute("SELECT setval('match_id_seq', (SELECT MAX(id) FROM match)+1);")
        cur.execute("SELECT setval('messages_id_seq', (SELECT MAX(id) FROM messages)+1);")
        cur.execute("SELECT setval('\"ProfilInterest_id_seq\"', (SELECT MAX(id) FROM \"ProfilInterest\")+1);")
        cur.execute("SELECT setval('search_id_seq', (SELECT MAX(id) FROM search)+1);")
        cur.execute("SELECT setval('visites_id_seq', (SELECT MAX(id) FROM visites)+1);")
        cur.execute("SELECT setval('profil_id_seq', (SELECT MAX(id) FROM profil)+1);")

        conn.commit()
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()