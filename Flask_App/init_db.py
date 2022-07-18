import os
import psycopg2

DB_USERNAME = "sammy"
DB_PASSWORD = "test"  

DBFILES = [
        "flask_db_public_users.sql",
        "flask_db_public_accountcontrol.sql",
        "flask_db_public_images.sql",
        "flask_db_public_Interest.sql",
        "flask_db_public_likes.sql",
        "flask_db_public_messages.sql",
        "flask_db_public_notifications.sql",
        "flask_db_public_ProfilInterest.sql",
        "flask_db_public_search.sql",
        "flask_db_public_location.sql",
        "flask_db_public_visites.sql",
        "flask_db_public_match.sql",
        "flask_db_public_profil.sql"
]

def executeScriptsFromFile(c):
        # Open and read the file as a single buffer
        # for file in DBFILES:
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
                try:
                        c.execute(command)
                except:
                        print("Command skipped: ", msg)
                conn.commit()

def main():
        conn = psycopg2.connect(
                host="localhost",
                database="flask_db",
                user=DB_USERNAME,
                password=DB_PASSWORD)

        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Execute a command: this creates a new table
        cur.execute('DROP TABLE IF EXISTS users;')
        cur.execute('DROP TABLE IF EXISTS accountcontrol;')
        cur.execute('DROP TABLE IF EXISTS images;')
        cur.execute('DROP TABLE IF EXISTS \"Interest\";')
        cur.execute('DROP TABLE IF EXISTS likes;')
        cur.execute('DROP TABLE IF EXISTS location;')
        cur.execute('DROP TABLE IF EXISTS match;')
        cur.execute('DROP TABLE IF EXISTS messages;')
        cur.execute('DROP TABLE IF EXISTS notifications;')
        cur.execute('DROP TABLE IF EXISTS \"ProfilInterest\";')
        cur.execute('DROP TABLE IF EXISTS search;')
        cur.execute('DROP TABLE IF EXISTS visites;')
        cur.execute('DROP TABLE IF EXISTS profil;')
        conn.commit()
        try:
                cur.execute('CREATE EXTENSION pgcrypto;')
        except:
                print("pgcrypto already exists") 
        executeScriptsFromFile(cur)
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
        
        conn.commit()
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()