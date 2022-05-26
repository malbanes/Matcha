from datetime import datetime, timedelta

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
        print(date_buffer)
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

