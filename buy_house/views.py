from django.shortcuts import render
from django.http import HttpResponse
from django.db import connections
from django.db.models import Q
from django.views import View
from buy_house.models import (JrA, JrB, JrC, JrD, JrE, JrF, JrG, JrH, JrI,
                            JrJ, JrK, JrM, JrN, JrO, JrP, JrQ, JrT, JrU,
                            JrV, JrW, JrX, JrZ, YES319, YungChing)
import json
import time
import pandas as pd
import requests
import random
import ast
from bs4 import BeautifulSoup as bs
from .utils import FindManInObjs, group_score, get_gkey, is_man
from .forms import GetItemsListForm
import os

# Create your views here.

all_city_dict = {"A": "臺北市", "B": "臺中市", "C": "基隆市", "D": "臺南市", "E": "高雄市", "F": "新北市", "G": "宜蘭縣", "H": "桃園市", "I": "嘉義市", "J": "新竹縣", "K": "苗栗縣", "M": "南投縣", "N": "彰化縣", "O": "新竹市", "P": "雲林縣", "Q": "嘉義縣", "T": "屏東縣", "U": "花蓮縣", "V": "臺東縣", "X": "澎湖縣", "W": "金門縣", "Z": "連江縣"}
jr_dict = {'臺北市': JrA, '臺中市': JrB, '基隆市': JrC, '臺南市': JrD, '高雄市': JrE, '新北市': JrF, '宜蘭縣': JrG, '桃園市': JrH, '嘉義市': JrI, '新竹縣': JrJ, '苗栗縣': JrK, '南投縣': JrM, '彰化縣': JrN, '新竹市': JrO, '雲林縣': JrP, '嘉義縣': JrQ, '屏東縣': JrT, '花蓮縣': JrU, '臺東縣': JrV, '金門縣': JrW, '澎湖縣': JrX, '連江縣': JrZ}
# jz_dict = {'臺北市': JzA, '臺中市': JzB, '基隆市': JzC, '臺南市': JzD, '高雄市': JzE, '新北市': JzF, '宜蘭縣': JzG, '桃園市': JzH, '嘉義市': JzI, '新竹縣': JzJ, '苗栗縣': JzK, '南投縣': JzM, '彰化縣': JzN, '新竹市': JzO, '雲林縣': JzP, '嘉義縣': JzQ, '屏東縣': JzT, '花蓮縣': JzU, '臺東縣': JzV, '金門縣': JzW, '澎湖縣': JzX, '連江縣': JzZ}
sqlite_dict = {'yes319': YES319, '永慶房屋' : YungChing }

def index(request):
    return HttpResponse('你好！要買屋給偶嗎')


def spider_form_view(request):
    success = False
    if request.method == 'POST':
        form = GetItemsListForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            agency_source = form.cleaned_data['agency_source']
            delay_seconds = form.cleaned_data['delay_seconds']

            # 整理參數
            run_city = ','.join(city)
            run_agency = ','.join(agency_source)
            # 調用爬蟲多線程
            path = 'work/house_agency/'
            command = f'python {path}thread.py -s {run_agency} -c {run_city}'
            print(command)
            # os.system(command)

            # 提交成功將表單清空，並回傳訊息
            success = True
            form = GetItemsListForm()
            status = 'OK'


    else:
        form = GetItemsListForm()
        status = 'NG'

    result = {
        'form' : form,
        'status' : status,
        'success': success
    }

    return render(request, 'createtasks.html', result)


class ObjCompare(View):
    TAG = '[ObjCompare]'

    # 參數 source:房源 city_code:縣市代碼
    # 比對今日爬取的物件編號，找出新物件做回傳
    def find_new_obj(request):
        source = request.GET.get('source',None)
        city_code = request.GET.get('city_code',None)
        city = all_city_dict[city_code]
        now_list = []
        today_list = []
        # 先抓出案源資料庫，該縣市同source的資料
        now = jr_dict[city].objects.filter(source=source).order_by('source_id').values('source_id')
        for n in now:
            now_list.append(n['source_id'])
        # 再從sqlite抓出今天抓取的資料
        today = sqlite_dict[source].objects.using('com_sqlite').filter(city=city).order_by('source_id').values('source_id')
        for t in today:
            today_list.append(t['source_id'])
        new_ids = [id for id in today_list if id not in now_list]
        # new_list = dict()
        # # 有新房源的話 把新id的資料從sqlite抓出來
        # if new_ids:
        #     print(f'{source}有{len(new_ids)}個新物件ID')
        #     print(new_ids)
        #     new_list = sqlite_dict[source].objects.using('com_sqlite').filter(source_id__in=new_ids).values()
        
        result = {
                'todo': 'New',
                'status' :'OK',
                'source' : source,
                'city_name': city,
                'new_ids' : new_ids,
                }
        
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type='application/json; charset=utf-8')


    # 參數 source:房源 city_code:縣市代碼
    # 比對今日爬取的物件編號，找出已下市的資料，並做處理
    #!! 執行前務必確認已將今日爬取的資料寫入sqlite資料庫
    def find_del_obj(request):
        source = request.GET.get('source',None)
        city_code = request.GET.get('city_code',None)
        city = all_city_dict[city_code]
        now_list = []
        today_list = []
        # 先抓出案源資料庫，該縣市同source的資料
        now = jr_dict[city].objects.filter(source=source).order_by('source_id').values('source_id')
        for n in now:
            now_list.append(n['source_id'])
        # 再抓出今天抓取的資料
        today = sqlite_dict[source].objects.using('com_sqlite').filter(city=city).order_by('source_id').values('source_id')
        for t in today:
            today_list.append(t['source_id'])
        
        # 找出失效物件
        del_list = [id for id in now_list if id not in today_list]
        update_time = time.strftime("%Y-%m-%d %H:%M:%S")
        if del_list:
            print(f'找到{source} {len(del_list)}個已失效的物件ID')
            del_ids = '"' + '","'.join(del_list) + '"'
            table_name = f'jr_{city_code.lower()}'
            # 更新資料庫的失效物件，is_delete改為1，及更新時間
            cursor = connections['default'].cursor()
            sql = f"UPDATE housecase.{table_name} SET is_delete = 1, update_time = '{update_time}' WHERE source = '{source}' AND source_id IN ({del_ids})"
            cursor.execute(sql)
            # 抓出失效物件中，是group_man的
            no_man_keys = jr_dict[city].objects.filter(source=source, is_delete=1, group_man=1).order_by('source_id').values('group_key')

            # 把失效的物件移到下市的表格
            del_table = f'jz_{city_code.lower()}'
            sql = f"""
            INSERT INTO housecase.{del_table} (`source`,`source_id`,`subject`,`city`,`area`,`road`,`address`,`situation`,
            `total`,`price_ave`,`feature`,`pattern`,`pattern1`,`total_ping`,`building_ping`,`att_ping`,`public_ping`,`land_ping`,
            `house_age`,`house_age_v`,`floor_web`,`floor`,`total_floor`,`house_num`,`blockto`,`house_type`,`manage_type`,`manage_fee`,
            `edge`,`dark`,`parking_type`,`lat`,`lng`,`link`,`img_url`,`contact_type`,`contact_man`,`phone`,`brand`,`branch`,`company`,
            `price_renew`,`insert_time`,`update_time`,`community`,`mrt`,`group_man`,`group_key`,`group_record`,`history`,`address_cal`,
            `is_delete`,`is_hidden`)
            SELECT `source`,`source_id`,`subject`,`city`,`area`,`road`,`address`,`situation`,
            `total`,`price_ave`,`feature`,`pattern`,`pattern1`,`total_ping`,`building_ping`,`att_ping`,`public_ping`,`land_ping`,
            `house_age`,`house_age_v`,`floor_web`,`floor`,`total_floor`,`house_num`,`blockto`,`house_type`,`manage_type`,`manage_fee`,
            `edge`,`dark`,`parking_type`,`lat`,`lng`,`link`,`img_url`,`contact_type`,`contact_man`,`phone`,`brand`,`branch`,`company`,
            `price_renew`,`insert_time`,`update_time`,`community`,`mrt`,`group_man`,`group_key`,`group_record`,`history`,`address_cal`,
            `is_delete`,`is_hidden`
            FROM housecase.{table_name} WHERE source = '{source}' AND is_delete = 1
            """
            cursor.execute(sql)
            sql = f"DELETE FROM housecase.{table_name} WHERE source = '{source}' AND is_delete = 1"
            cursor.execute(sql)
            print(f'已将{source}失效物件移至下市表格{del_table}')
            
            for item in no_man_keys:
                gkey = item['group_key']
                # 防止先前其他錯誤資料，先確定key裡沒有man
                sql = f"UPDATE housecase.{table_name} SET group_man = 0 WHERE group_key = '{gkey}'"
                # cursor.execute(sql)
                # 先把這個group中的有效物件抓出來，丟進去找新的man
                find_man_objs = jr_dict[city].objects.filter(group_key=gkey, is_delete=0).values()
                if find_man_objs:
                    win_obj = FindManInObjs(find_man_objs)
                    print(win_obj)
                    if win_obj:
                        win_sn = win_obj['sn']
                        sql = f"UPDATE housecase.{table_name} SET group_man = 1 WHERE sn = '{win_sn}'"
                        # cursor.execute(sql)
                        print(f'{gkey}已選出新的group_man! SN:{win_sn}')
                else:
                    print(f'{gkey}中無其他物件！')

        result = {
                'todo': 'Del',
                'status' :'OK',
                'source' : source,
                'city_name': city,
                'del_id' : del_list,
                'update_time' : update_time
                }
        
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type='application/json; charset=utf-8')
    
    def price_update(request):
        source = request.GET.get('source',None)
        city_code = request.GET.get('city_code',None)
        city = all_city_dict[city_code]
        # 先抓出案源資料庫，該縣市同source的資料
        now_info = jr_dict[city].objects.filter(source=source).order_by('source_id').values('sn','source_id', 'total', 'history', 'subject', 'link')
        now_info_df = pd.DataFrame.from_records(now_info)
        # 再抓出今天抓取的資料
        today_info = sqlite_dict[source].objects.using('com_sqlite').filter(city=city).order_by('source_id').values('source_id','re_price')
        today_info_df = pd.DataFrame.from_records(today_info)

        # 合併兩個表格，根據'source_id'欄位進行合併
        merged_df = pd.merge(today_info_df, now_info_df, on='source_id')

        # 篩選出total不一致的資料 
        ##!兩邊資料的格式都要是int，不能是文字或float
        new_info = merged_df[merged_df['re_price'] != merged_df['total']]

        # 將MYSQL舊價格的total欄位刪除
        new_info = new_info.drop(columns=['total'])
        # 重新命名新抓到的價格re_price欄位為total
        new_info = new_info.rename(columns={'re_price': 'total'})

        #將更新的資料寫入資料庫
        cursor = connections['default'].cursor()
        table_name = f'jr_{city_code.lower()}'
        for index, obj in new_info.iterrows():
            new_total = obj['total']
            source_id = obj['source_id']
            subject = obj['subject']
            link = obj['link']
            sn = obj['sn']
            insert_time = time.strftime("%Y-%m-%d")
            add_his = ',{' + f'"source":"{source}","source_id":"{source_id}","total":"{new_total}","subject":"{subject}","insert_time":"{insert_time}","link":"{link}"' + '}]'
            now_his = obj['history'].rstrip(']')
            history = now_his + add_his
            update_time = time.strftime("%Y-%m-%d %H:%M:%S")
            # 一般建物計算方式
            sql = f""" 
            UPDATE housecase.{table_name} 
            SET total = {new_total}, price_renew = 1, price_ave = round(total/total_ping, 2), history = '{history}', update_time = '{update_time}'
            WHERE sn = '{sn}' AND total_ping !=0 ;
            """
            # cursor.execute(sql)
            # 土地計算方式
            sql = f""" 
            UPDATE housecase.{table_name} 
            SET total = {new_total}, price_renew = 1, price_ave = round(total/land_ping, 2), history = '{history}', update_time = '{update_time}'
            WHERE sn = '{sn}' AND total_ping =0 AND land_ping!=0 ;
            """
            # cursor.execute(sql)
            # 資料不完全的物件平均單價寫0
            sql = f""" 
            UPDATE housecase.{table_name} 
            SET total = {new_total}, price_renew = 1, price_ave = 0, history = '{history}', update_time = '{update_time}'
            WHERE sn = '{sn}' AND total_ping =0 AND land_ping=0 ;
            """
            # cursor.execute(sql)
            print(f'{table_name}表 {source} ID:{source_id} 價格已更新至資料庫')
        

        updated_ids = [obj["source_id"] for obj in new_info.to_dict(orient='records')]
        result = {
                'todo': 'UPDATE',
                'status' :'OK',
                'source' : source,
                'city_name': city,
                'updated_ids' : updated_ids,
                }
        
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type='application/json; charset=utf-8')
    

    def get_noaddr_keys(request):
        source = request.GET.get('source',None)
        city_code = request.GET.get('city_code',None)
        city = all_city_dict[city_code]
        group_keys = jr_dict[city].objects.filter(source=source, group_man = 1, address_cal = '').values('group_key')

        key_list = [key['group_key'] for key in group_keys]
        result = {
        'todo': 'FIND_ADDR',
        'status' :'OK',
        'source' : source,
        'city_name': city,
        'group_keys' : key_list,
        }

        params = {
            'group_keys' : key_list,
            'city_code' : city_code
        }
        api_url = 'http://127.0.0.1:8000/buy_house/addr_update'
        requests.get(api_url, params=params)
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type='application/json; charset=utf-8')


    def addr_update(request):
        group_keys = request.GET.get('group_keys',None)
        city_code = request.GET.get('city_code',None)
        city = all_city_dict[city_code]
        keys = ast.literal_eval(group_keys)
        addr_records = []

        houses = jr_dict[city].objects.filter(group_key__in = keys)

        for house in houses:
            if house.total_ping == 0:
                min_total_ping, max_total_ping = '',''
            else:
                min_total_ping = house.total_ping - 0.2
                max_total_ping = house.total_ping + 0.2
            if house.building_ping == 0:
                min_main_ping, max_main_ping = '',''
            else:
                min_main_ping = house.building_ping - 0.2
                max_main_ping = house.building_ping + 0.2
            if house.att_ping == 0:
                min_attach_ping, max_attach_ping = '',''
            else:
                min_attach_ping = house.att_ping - 0.2
                max_attach_ping = house.att_ping + 0.2
            if house.public_ping == 0:
                min_public_ping, max_public_ping = '',''
            else:
                min_public_ping = house.public_ping - 0.2
                max_public_ping = house.public_ping + 0.2
            if house.floor < 0:
                min_level, max_level = '',''
            else:
                min_level = house.floor
                max_level = house.floor
            if house.total_floor < 0:
                min_total_level, max_total_level = '',''
            else:
                min_total_level = house.total_floor
                max_total_level = house.total_floor
            min_age = house.house_age_v - 1.5
            if min_age < 0:
                min_age = ''
            max_age = house.house_age_v + 1.5
            api_url = 'http://land-data.yeshome.net.tw/build_data/find_possible_addrs_sc/'
            params = {
                'token':'7079e8b7-a5a3-415d-ab66-38f8cf5cdcbc',
                'city_name': house.city,
                'area_name': house.area,
                'road': house.road,
                'min_total_ping': min_total_ping,
                'max_total_ping': max_total_ping,
                'min_main_ping': min_main_ping,
                'max_main_ping': max_main_ping,
                'min_attach_ping': min_attach_ping,
                'max_attach_ping': max_attach_ping,
                'min_public_ping': min_public_ping,
                'max_public_ping': max_public_ping,
                'min_level': min_level,
                'max_level': max_level,
                'min_total_level': min_total_level,
                'max_total_level': max_total_level,
                'min_age': min_age,
                'max_age': max_age
            }
            time.sleep(random.uniform(2,7))
            api_res = requests.get(api_url, params=params)
            result = bs(api_res.text, 'lxml').find('p').text.replace("'",'"')
            jr_dict[city].objects.filter(group_key=house.group_key).update(address_cal = result)
            addr_records.append({'group_key': house.group_key, 'address_cal': result})

        result = {
        'todo': 'ADDR_UPDATE',
        'status' :'OK',
        'keys_addr' : addr_records,
        }

        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type='application/json; charset=utf-8')
    
    def find_group(request):
        source = request.GET.get('source',None)
        city_code = request.GET.get('city_code',None)
        city = all_city_dict[city_code]
        # 先找出無家可歸的孩子們
        no_group = jr_dict[city].objects.filter(source=source, group_key = '').values()

        # 從案源資料庫抓「同行政區」、「價格正負10%」、「road一樣或為空」、「是group_man」的物件出來
        for obj in no_group:
            print(f'{source} Source_id:' + obj['source_id'] + ' 開始找Group')
            pass2_sn = [] # 第二階段通過的GROUP列表
            # 土地以外的比對group方式
            if '地' not in obj['house_type']:
                # 作為第一階段的篩選
                pass1_df = jr_dict[city].objects.filter(
                    (Q(road=obj['road']) | Q(road='')),
                    area=obj['area'],
                    total__range=(obj['total'] * 0.9 , obj['total'] * 1.1),
                    group_man=1
                    ).values()
                for man in pass1_df:
                    score = group_score(obj, man)
                    compare_key = man['group_key']
                    # print(f'比對Group_Key:{compare_key}獲得{score}分')
                    if score >= 35:
                        pass2_sn.append({"key":compare_key, "score":score})
            # 土地的計算分數方式
            else:
                min_land_ping = obj['land_ping'] - 2
                max_land_ping = obj['land_ping'] + 2
                check_cloumns = ['total', 'road', 'lat', 'lng', 'land_ping', 'total_ping']

                pass1_df = jr_dict[city].objects.filter(
                    (Q(road=obj['road']) | Q(road='')),
                    (Q(land_ping__range=(min_land_ping, max_land_ping)) | Q(total_ping__range=(min_land_ping, max_land_ping))),
                    area=obj['area'],
                    total__range=(obj['total'] * 0.9 , obj['total'] * 1.1),
                    group_man=1
                    ).values()

                for row in pass1_df:
                    point = 0
                    if obj['land_ping'] == row['total_ping'] or obj['total_ping'] == row['land_ping']:
                        point += 2
                    for column in check_cloumns:
                        if obj[column] == row[column]:
                            point += 1
                            if column in ['lat', 'lng', 'land_ping'] and obj[column]!=0:
                                point += 2
                    compare_key = row['group_key']
                    # print(f'比對Index{index} Group_Key:{compare_key}獲得{point}分')
                    pass2_sn.append({"key":compare_key, "score":point})

            table_name = f'jr_{city_code.lower()}'
            cursor = connections['default'].cursor()
            # 沒找到group的，自組一個新group，並成為group_man
            if len(pass2_sn) == 0:
                print('比對不到Group,自組新key')
                obj_key = get_gkey()
                obj_man = 1
                old_record = '{'
            elif len(pass2_sn) == 1:
                obj_key = pass2_sn[0]['key']
                man = jr_dict[city].objects.filter(group_man=1, group_key=obj_key).values()
                old_record = man[0]['group_record']
                if old_record == '[]':
                    old_record = '{'
                else:
                    old_record = old_record[:-1] + ','
                obj_man = is_man(obj, man)
                if obj_man :
                    # 先把這個key原本的man改0，再寫入這筆
                    sql = f" UPDATE housecase.{table_name} SET group_man = 0 WHERE group_key = '{obj_key}' AND group_man = 1 "
                    # cursor.execute(sql)
            else: # 有多個找最高分
                obj_key = max(pass2_sn, key=lambda x: x['score'])['key']
                man = jr_dict[city].objects.filter(group_man=1, group_key=obj_key).values()
                old_record = man[0]['group_record']
                if old_record == '[]':
                    old_record = '{'
                else:
                    old_record = old_record[:-1] + ','
                obj_man = is_man(obj, man)
                if obj_man :
                    sql = f" UPDATE housecase.{table_name} SET group_man = 0 WHERE group_key = '{obj_key}' AND group_man = 1 "
                    # cursor.execute(sql)
            
            print(f'加入group囉！GROUP KEY:{obj_key}')
            source = obj['source']
            date = time.strftime("%Y-%m-%d")
            obj_sn = obj['sn']
            link = obj['link']
            price = obj['total']
            record =f'"{source}":' + '{' + f'"public":"{date}","sn":"{obj_sn}","wbsite":"{link}","price":"{price}"' + '}}'
            new_record = old_record + record
            # print(new_record)
            sql = f" UPDATE housecase.{table_name} SET group_man = {obj_man} , group_key = '{obj_key}' WHERE sn = {obj_sn} ; "
            # cursor.execute(sql)
            
            # 更新此group內所有物件的group_record、address_cal
            sql = f" SELECT address_cal FROM housecase.{table_name} WHERE group_man = 1 AND group_key = '{obj_key}' ; "
            cursor.execute(sql)
            is_add = cursor.fetchone()
            copy_add = is_add[0].replace("'",'"') if is_add else ''
            sql = f" UPDATE housecase.{table_name} SET group_record = '{new_record}', address_cal = '{copy_add}' WHERE group_key = '{obj_key}'; "
            # cursor.execute(sql)

        return HttpResponse(f'{source} {city}資料，皆已找完Group!')
