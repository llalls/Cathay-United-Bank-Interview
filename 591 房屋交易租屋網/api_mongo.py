from flask import Flask, jsonify, request, make_response
from flask_pymongo import PyMongo
from flask_mongoengine import MongoEngine
from mongoengine import StringField, IntField
from urllib import parse
import json




app = Flask(__name__)

app.config["MONGO_DBNAME"] = "HouseDB"
app.config['MONGO_URI'] = "mongodb://localhost:27017/HouseDB"
mongo = PyMongo(app)


# Condition 1: 針對「承租者性別」與「租屋地址」篩選
@app.route('/by_sex_addr', methods=['GET', 'POST'])
def by_sex_addr():
    house_collections = mongo.db.HouseCollection
    # house_collections = mongo.db.HouseCollectionTest
    
    _json = request.get_json(force=True)
    sex = _json["sex"]          # 男生, 女生, 男女生皆可
    location = _json['addr']    # 台北, 新北
    houseList = []

    for hc in house_collections.find():
        if hc['sex'].find(sex) != -1 or hc['sex'] == None:
            if hc['addr'].find(location) != -1:
                houseList.append({
                    'info':hc['info'], 
                    'info_identity':hc['info_identity'], 
                    'phone':hc['phone'],
                    'room_type':hc['room_type'], 
                    'status':hc['status'], 
                    'sex':hc['sex'], 
                    'addr':hc['addr']
                })
    return jsonify({'result' : houseList})

# Condition 2: 針對「連絡電話」篩選
@app.route('/by_phone', methods=['POST', 'GET'])
def by_phone():
    house_collections = mongo.db.HouseCollection
    # house_collections = mongo.db.HouseCollectionTest

    _json = request.get_json(force=True)
    phone = _json['phone']          # 連絡電話
    phoneList = []

    for hc in house_collections.find():
        if hc['phone'] == str(phone):
            phoneList.append({
                'info':hc['info'], 
                'info_identity':hc['info_identity'], 
                'phone':hc['phone'],
                'room_type':hc['room_type'], 
                'status':hc['status'], 
                'sex':hc['sex'], 
                'addr':hc['addr']
            })
    return jsonify({'result' : phoneList})


# Condition 3: 針對「身分」篩選
@app.route('/by_infoIdentity', methods=['POST', 'GET'])
def by_infoIdentity():
    house_collections = mongo.db.HouseCollection
    # house_collections = mongo.db.HouseCollectionTest

    _json = request.get_json(force=True)
    identity = _json['info_identity']       # 屋主, 仲介
    houseList = []

    for hc in house_collections.find():
        if hc['info_identity'] == identity:
            houseList.append({
                'info':hc['info'], 
                'info_identity':hc['info_identity'], 
                'phone':hc['phone'],
                'room_type':hc['room_type'], 
                'status':hc['status'], 
                'sex':hc['sex'], 
                'addr':hc['addr']
            })
    return jsonify({'result' : houseList})

# Condition 4: 針對「地區」, 「屋主性別」與「屋主姓氏」篩選
@app.route('/by_addr_infoSex_infoName', methods=['POST', 'GET'])
def by_addr_infoSex_infoName():
    _json = request.get_json(force=True)
    house_collections = mongo.db.HouseCollection
    # house_collections = mongo.db.HouseCollectionTest
    
    houseList = []
    info_name = _json['info_name']      # 屋主姓氏
    info_sex = _json['info_sex']        # 屋主性別
    location = _json['addr']            # 地區

    if info_sex == "男生":
        titleOne, titleTwo = '先生', '伯伯'
    else:
        titleOne, titleTwo = '小姐', '太太'

    for hc in house_collections.find():
        if hc['addr'].find(location) != -1:
            if hc['info'].find(info_name) != -1 or info_name == None:
                if hc['info'].find(titleOne) != -1 or hc['info'].find(titleTwo) != -1:
                    houseList.append({
                        'info':hc['info'], 
                        'info_identity':hc['info_identity'], 
                        'phone':hc['phone'],
                        'room_type':hc['room_type'], 
                        'status':hc['status'], 
                        'sex':hc['sex'], 
                        'addr':hc['addr']
                    })

    return jsonify({'result' : houseList})


# 新增租屋資訊
@app.route('/add', methods=['POST'])
def add_HouseInfo():
    _json = request.json
    info = _json['info']
    info_identity = _json['info_identity']
    phone = _json['phone']
    room_type = _json['room_type']
    status = _json['status']
    sex = _json['sex']
    addr = _json['addr']

    if info and info_identity and phone and room_type and status and sex and addr and request.method == 'POST':
        id = mongo.db.HouseCollection.insert({
            'info':info, 
            'info_identity':info_identity, 
            'phone':phone,
            'room_type':room_type, 
            'status':status, 
            'sex':sex, 
            'addr':addr
        })
        resp = jsonify("House info added success")
        resp.status_code = 200
        return resp


if __name__ == "__main__":
    app.run(debug=True)