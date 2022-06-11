from flask_login import current_user
from __init__ import get_db_connection


def set_gender_orientation():
    #Select right Gender
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT genre_id, orientation_id FROM profil WHERE user_id=%(id)s LIMIT 1;", {'id': current_user.id})
    user_details = cur.fetchone()
    if user_details[0] == 1:
        # Si l'user est Hetero
        if user_details[1] == 1:
            #select femme et (hetero ou bi) ou non-binaire  A
            select_gender = "AND (genre_id=2 AND (orientation_id=1 or orientation_id=0) OR genre_id=0)"
        #si user est un homme gay
        elif user_details[1] == 2:
            #select homme et (gay ou bi) ou non binaire  B
            select_gender = "AND (genre_id=1 AND (orientation_id=0 or orientation_id=2) OR genre_id=0)"
        #si user est un homme bi
        elif user_details[1] == 0:
            #select homme et (gay ou bi) ou femme et (hetero ou bi) ou non binaire  B + A
            select_gender = "AND (genre_id=1 AND (orientation_id=0 or orientation_id=2) OR genre_id=2 AND (orientation_id=1 or orientation_id=0) OR genre_id=0)"
    elif user_details[0] == 2:
        #si user est une femme et hetero
        if user_details[1] == 1:
            #select homme et (hetero ou bi) ou non-binaire C
            select_gender = "AND (genre_id=1 AND (orientation_id=1 or orientation_id=0) OR genre_id=0)"
        #si user est une femme et gay
        elif user_details[1] == 2:
            #select femme et (gay ou bi) ou non-binaire D
            select_gender = "AND (genre_id=2 AND (orientation_id=0 or orientation_id=2) OR genre_id=0)"
        #si user est une femme et bi
        elif user_details[1] == 0:
            #select homme et (hetero ou bi) ou femme et (gay ou bi) ou non-binaire C + D
            select_gender = "AND (genre_id=1 AND (orientation_id=0 or orientation_id=2) OR genre_id=2 AND (orientation_id=1 or orientation_id=0) OR genre_id=0)"
    #si user est non-binaire et hetero
    elif user_details[1] == 1:
        #select homme et femme hetero
        select_gender = "AND orientation_id=1"
    #si user est non-binaire gay
    elif user_details[1] == 2:
        #select homme et femme gay
        select_gender = "AND orientation_id=2"
    #si user est non-binaire et bi
    elif user_details[1] == 0:
        #select all
        select_gender=""

    cur.close()
    conn.close()
    return select_gender