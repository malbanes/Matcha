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
    updated_score  = updated_score + (likes_num_after_last_co * 100)
    # if 1 tag + 10
    # if 5 tags  or  more +50
    if tag_num == 0:
        updated_score = updated_score - 20
    elif tag_num <= 5 and  tag_num > 0:
        updated_score = updated_score + (tag_num * 10)
    else: 
        updated_score = updated_score + (5 * 10)
    # If blocked -20
    updated_score = updated_score + (block_num * 20)
    # If reported -10
    updated_score = updated_score + (report_num * 10)
    # if  active -7 days +50
    # if  active +7 days -50
    date_buffer = datetime.now() - timedelta(days=7)
    if (date_buffer < lact_co_date) == True
        updated_score = updated_score + 50
    else:
        updated_score = updated_score - 50
    # if  match  +150
    updated_score = updated_score + (match_num  * 150)

    final_score = ((updated_score * 100 / 9999) + former_score) / 2
    return(final_score)

