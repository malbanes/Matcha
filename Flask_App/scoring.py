from datetime import datetime, timedelta
from __init__ import get_db_connection
from flask_login import current_user
from localization import distance
from age_calc import age
from gender_id import set_gender_orientation


def scoring_calculation(former_score, image_num, likes_num, tag_num, block_num, report_num, lact_co_date, match_num):
    #max 9999
    updated_score =  0
    #if no photo -20
    # 1 photo  +10
    # 2 photo  +20
    # 3 photo  +30
    # 4 photo  +40
    # 5 photo  +50
    if image_num == 0:
        updated_score = updated_score - 50
    else:
        updated_score = updated_score + (image_num * 10)
    # If like + 100
    updated_score  = updated_score + (likes_num * 100)
    # if 1 tag + 10
    # if 5 tags  or  more +50
    if tag_num == 0:
        updated_score = updated_score
    elif tag_num <= 5 and  tag_num > 0:
        updated_score = updated_score + (tag_num * 10)
    else: 
        updated_score = updated_score + (5 * 10)
    # If blocked -10
    updated_score = updated_score + (block_num * 10)
    # If reported -20
    updated_score = updated_score + (report_num * 20)
    # if  active -7 days +50
    # if  active +7 days -50
    try:
        date_buffer = datetime.now() - timedelta(days=7)
        if (date_buffer.date() < lact_co_date) == True:
            updated_score = updated_score + 50
            print("recent")
        else:
            updated_score = updated_score - 50
    except:
        print("Never connected")
    # if  match  +150
    updated_score = updated_score + (match_num  * 150)
    if updated_score < 0:
        updated_score = 0
    final_score = (updated_score + former_score) / 2
    if final_score > 9999:
        final_score = 9999
    elif final_score < 0:
        final_score =  0
    return(final_score)

def matching_calculation(orientation, long, lat, city, interest_num, birthdate, popularity_score):
    # orientation, long, lat, city  popularity_score return ceux de la db
    # Interest num = nombre d'intérets
    # age = age du user pas date de naissance
    
    conn = get_db_connection()
    cur = conn.cursor()
    #Select right Gender
    select_gender= set_gender_orientation()
    cur.execute("SELECT * FROM profil WHERE user_id != {0} {1}".format(current_user.id, select_gender))
    users = cur.fetchall()
    user_score = 0

    for user in users:
        if orientation == user[3]:
            user_score += 60
        cur.execute("SELECT latitude, longitude, city FROM location WHERE id=%(location_id)s LIMIT 1", {'location_id': user[4]})
        location_user = cur.fetchone()
        distance_from_user = distance(lat, long, location_user[0], location_user[1])
        if city == location_user[2]:
            user_score += 50
        elif distance_from_user <= 7500:
            user_score += 40 
        elif distance_from_user <= 15000 and distance_from_user > 7500:
            user_score += 30
        
        cur.execute("Select COUNT(pi.id) FROM profil LEFT JOIN \"ProfilInterest\" as pi ON profil.user_id = pi.user_id AND pi.user_id = %(targeted_user)s AND pi.interest_id IN (SELECT interest_id FROM \"ProfilInterest\" WHERE user_id=%(current_user_id)s ) GROUP BY profil.user_id ORDER BY COUNT(pi.id) desc LIMIT 1", {'targeted_user': user[1], 'current_user_id': current_user.id})
        hastag_interest_num = cur.fetchone()[0]
        if interest_num == hastag_interest_num:
            user_score += 40
        elif hastag_interest_num > 0:
            user_score += 30
        
        if age(user[5]) != 'N/A' and birthdate != 'N/A':
            minus_targeted_user_age = int(age(user[5])) - 5
            max_targeted_user_age = int(age(user[5])) + 5

            if birthdate == age(user[5]):
                user_score += 30
            elif birthdate >= minus_targeted_user_age and birthdate <= max_targeted_user_age:
                user_score += 20

        if popularity_score <= (user[8] + 500) and popularity_score >= (user[8] - 500):
            user_score += 20
        elif popularity_score <= (user[8] + 500) and popularity_score >= (user[8] - 500):
            user_score += 15
        elif popularity_score <= (user[8] + 1000) and popularity_score >= (user[8] - 1000):
            user_score += 10

        user_score = user_score / 2
        if user_score > 25:
            print("LETS GO INERT USER INTO MATCHING LIST")
            cur.execute("INSERT INTO match (user_id, match_id, score) VALUES (%(user_id)s, %(match_id)s, %(score)s)", {'user_id': current_user.id, 'match_id': user[1], 'score': int(user_score)})
            conn.commit()
        user_score = 0
    cur.close()
    conn.close()