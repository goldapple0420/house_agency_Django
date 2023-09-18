import re, uuid

# 如果這個key沒有man，要從整個group裡面找出man，請示先將這個group裡所有obj丟到一個pandas df
def FindManInObjs(find_man_objs):
    max_score = 1
    im_man = dict()
    for obj in find_man_objs:
        obj_score = 0
        if obj['road'] != '':
            obj_score+=3
        if obj['situation'] != '':
            obj_score+=1
        if obj['feature'] != '':
            obj_score+=1
        if obj['pattern'] != '':
            obj_score+=3
        if obj['total_ping'] != 0:
            obj_score+=2
        if obj['building_ping'] != 0:
            obj_score+=2
        if obj['att_ping'] != 0:
            obj_score+=2
        if obj['public_ping'] != 0:
            obj_score+=2
        if obj['land_ping'] != 0:
            obj_score+=2
        if obj['house_age_v'] != 0:
            obj_score+=2
        if obj['floor'] != 0:
            obj_score+=2
        if obj['total_floor'] != 0:
            obj_score+=2
        if obj['house_num'] != 0:
            obj_score+=1
        if obj['blockto'] != '':
            obj_score+=1
        if obj['house_type'] != '':
            obj_score+=2
        if obj['manage_type'] != '':
            obj_score+=1
        if obj['manage_fee'] != '':
            obj_score+=1
        if obj['edge'] != '':
            obj_score+=1
        if obj['dark'] != '':
            obj_score+=1
        if obj['parking_type'] != '':
            obj_score+=1
        if obj['lat'] != 0:
            obj_score+=3
        if obj['lng'] != 0:
            obj_score+=3
        if obj['img_url'] != '':
            obj_score+=1
        if obj['contact_man'] != '':
            obj_score+=1
        if obj['phone'] != '':
            obj_score+=2
        if obj['brand'] != '':
            obj_score+=1
        if obj['branch'] != '':
            obj_score+=2
        if obj['community'] != '':
            obj_score+=2
        
        if obj_score > max_score:
            max_score = obj_score
            im_man = {"sn":obj['sn'], "group_key":obj['group_key'], "score":obj_score}
    
    # 將最終候選人的sn回傳
    return im_man

# 計算建物比對Group的分數，obj是候選人，man是現任group_man
def group_score(obj, man):
    score = 0
    # 格局拆成房數、廳數、衛浴數
    match = re.findall(r'(\d+)房', obj['pattern'])
    obj_room = int(match[0]) if match else 0
    match = re.findall(r'(\d+)房', man['pattern'])
    man_room = int(match[0]) if match else 0
    
    match = re.findall(r'(\d+)廳', obj['pattern'])
    obj_hall = int(match[0]) if match else 0
    match = re.findall(r'(\d+)廳', man['pattern'])
    man_hall = int(match[0]) if match else 0

    match = re.findall(r'(\d+)衛', obj['pattern'])
    obj_toilet = int(match[0]) if match else 0
    match = re.findall(r'(\d+)衛', man['pattern'])
    man_toilet = int(match[0]) if match else 0
    
    # 東森房屋僅提供主建物+附屬建物坪數，沒有個別提供主建物跟附屬建物
    if obj['source'] == '東森房屋':
        man['building_ping'] = man['building_ping'] + man['att_ping']

    # 非土地類的計算方式，滿分55分，得分高於35分，則將物件加入這group，若與多個group分數高於35，則取最高分的group加入
    if obj['road'] != '' and man['road'] != '':
        score+=5
    if obj['address'] == man['address']:
        score+=5
    if obj_room == man_room:
        score+=2
    if obj_hall == man_hall:
        score+=2
    if obj_toilet == man_toilet:
        score+=2
    if obj['total_ping'] == man['total_ping']:
        score+=4
    if obj['building_ping'] == man['building_ping']:
        score+=3
    if obj['att_ping'] == man['att_ping']:
        score+=3
    if obj['public_ping'] == man['public_ping']:
        score+=3
    if obj['land_ping'] == man['land_ping']:
        score+=4
    if obj['house_age_v'] == man['house_age_v']:
        score+=3
    if (man['house_age_v']-2 <= obj['house_age_v']) or (obj['house_age_v'] <= man['house_age_v']+2):
        score+=1
    if obj['floor'] == man['floor']:
        score+=3
    if obj['total_floor'] == man['total_floor']:
        score+=3
    if (obj['lat'] == man['lat']) and (obj['lng'] == man['lng']):
        score+=8
    if obj['house_type'] == man['house_type']:
        score+=4
    
    #如果房屋類型是大樓、電梯大樓、華廈，floor一定要一樣，怕是不同物件，但若是同社區，格局坪數地址位置可能都一樣
    if '大樓' in obj['house_type'] or '華夏' in obj['house_type']:
        if obj['floor'] != man['floor']:
            score = 0
    
    return score

def get_gkey():
    unique_id = uuid.uuid4()
    key = 'yh' + str(unique_id).replace('-', '')
    return key

# 計算此物件能不能成為group_man（資料完整度有沒有贏過目前的group_man）
def is_man(obj, man):
    obj_score = 0
    man_score = 0

    # 算分數方式寫這
    if '地' not in obj['house_type']:
        # 先算要來比賽當man的Group新成員
        if obj['road'] != '':
            obj_score+=3
        if obj['situation'] != '':
            obj_score+=1
        if obj['feature'] != '':
            obj_score+=1
        if obj['pattern'] != '':
            obj_score+=3
        if obj['total_ping'] != 0:
            obj_score+=2
        if obj['building_ping'] != 0:
            obj_score+=2
        if obj['att_ping'] != 0:
            obj_score+=2
        if obj['public_ping'] != 0:
            obj_score+=2
        if obj['land_ping'] != 0:
            obj_score+=2
        if obj['house_age_v'] != 0:
            obj_score+=2
        if obj['floor'] != 0:
            obj_score+=2
        if obj['total_floor'] != 0:
            obj_score+=2
        if obj['house_num'] != 0:
            obj_score+=1
        if obj['blockto'] != '':
            obj_score+=1
        if obj['house_type'] != '':
            obj_score+=2
        if obj['manage_type'] != '':
            obj_score+=1
        if obj['manage_fee'] != '':
            obj_score+=1
        if obj['edge'] != '':
            obj_score+=1
        if obj['dark'] != '':
            obj_score+=1
        if obj['parking_type'] != '':
            obj_score+=1
        if obj['lat'] != 0:
            obj_score+=3
        if obj['lng'] != 0:
            obj_score+=3
        if obj['img_url'] != '':
            obj_score+=1
        if obj['contact_man'] != '':
            obj_score+=1
        if obj['phone'] != '':
            obj_score+=2
        if obj['brand'] != '':
            obj_score+=1
        if obj['branch'] != '':
            obj_score+=2
        if obj['community'] != '':
            obj_score+=2
        
        # 再來算目前的Group man的分數
        if man[0]['road'] != '':
            man_score+=3
        if man[0]['situation'] != '':
            man_score+=1
        if man[0]['feature'] != '':
            man_score+=1
        if man[0]['pattern'] != '':
            man_score+=3
        if man[0]['total_ping'] != 0:
            man_score+=2
        if man[0]['building_ping'] != 0:
            man_score+=2
        if man[0]['att_ping'] != 0:
            man_score+=2
        if man[0]['public_ping'] != 0:
            man_score+=2
        if man[0]['land_ping'] != 0:
            man_score+=2
        if man[0]['house_age_v'] != 0:
            man_score+=2
        if man[0]['floor'] != 0:
            man_score+=2
        if man[0]['total_floor'] != 0:
            man_score+=2
        if man[0]['house_num'] != 0:
            man_score+=1
        if man[0]['blockto'] != '':
            man_score+=1
        if man[0]['house_type'] != '':
            man_score+=2
        if man[0]['manage_type'] != '':
            man_score+=1
        if man[0]['manage_fee'] != '':
            man_score+=1
        if man[0]['edge'] != '':
            man_score+=1
        if man[0]['dark'] != '':
            man_score+=1
        if man[0]['parking_type'] != '':
            man_score+=1
        if man[0]['lat'] != 0:
            man_score+=3
        if man[0]['lng'] != 0:
            man_score+=3
        if man[0]['img_url'] != '':
            man_score+=1
        if man[0]['contact_man'] != '':
            man_score+=1
        if man[0]['phone'] != '':
            man_score+=2
        if man[0]['brand'] != '':
            man_score+=1
        if man[0]['branch'] != '':
            man_score+=2
        if man[0]['community'] != '':
            obj_score+=2
    # 土地類的計算方式
    else:
        # 先算要來比賽當man的Group新成員
        if obj['road'] != '':
            obj_score+=5
        if obj['situation'] != '':
            obj_score+=1
        if obj['feature'] != '':
            obj_score+=1
        if obj['total_ping'] != 0:
            obj_score+=3
        if obj['land_ping'] != 0:
            obj_score+=4
        if obj['lat'] != 0:
            obj_score+=4
        if obj['lng'] != 0:
            obj_score+=4
        if obj['img_url'] != '':
            obj_score+=1
        if obj['contact_man'] != '':
            obj_score+=1
        if obj['phone'] != '':
            obj_score+=2
        if obj['brand'] != '':
            obj_score+=1
        if obj['branch'] != '':
            obj_score+=2
        
        # 再來算目前的Group man的分數
        if man[0]['road'] != '':
            man_score+=5
        if man[0]['situation'] != '':
            man_score+=1
        if man[0]['feature'] != '':
            man_score+=1
        if man[0]['total_ping'] != 0:
            man_score+=3
        if man[0]['land_ping'] != 0:
            man_score+=4
        if man[0]['lat'] != 0:
            man_score+=4
        if man[0]['lng'] != 0:
            man_score+=4
        if man[0]['img_url'] != '':
            man_score+=1
        if man[0]['contact_man'] != '':
            man_score+=1
        if man[0]['phone'] != '':
            man_score+=2
        if man[0]['brand'] != '':
            man_score+=1
        if man[0]['branch'] != '':
            man_score+=2

    # 0: group_man不變 1:此obj贏過原本的group_man，當選新的group_man
    if obj_score <= man_score:
        return 0
    else:
        return 1