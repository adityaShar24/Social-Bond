from flask import request , json , make_response
from models.user_model import User
from models.make_request_model import Request
from database.mongo import request_collection
from flask_jwt_extended import create_access_token
from utils.constants import HTTP_201_CREATED , HTTP_400_BAD_REQUEST , USER_REGISTERED_MESSAGE , INVALID_PASSWORD_ERROR , REQUEST_SENT_MESSAGE
import bson.json_util as json_util
import datetime
from bson.objectid import ObjectId

def register():
    body = json.loads(request.data)
    
    username = body['username']
    password = body['password']
    
    user = User(username , password)
    
    saved_users = user.save_user()
    json_version = json_util.dumps(saved_users)
    
    return make_response({'message': USER_REGISTERED_MESSAGE.format(username = username), 'user': json_version} , HTTP_201_CREATED)

def login():
    body = json.loads(request.data)
    username = body['username']
    password = body['password']
    
    user = User.find_by_username(username)
        
    if password != user['password']:
        return make_response({'message':INVALID_PASSWORD_ERROR} , HTTP_400_BAD_REQUEST)
    
    access_token = create_access_token(identity=username , fresh=datetime.timedelta(minutes=30))
    
    return make_response({'message':{'access token':access_token}} , HTTP_201_CREATED)

def make_request():
    body = json.loads(request.data)
    From = body['From']
    to = body['to']
    
    request_instance = Request(From , to)
    request_id = request_instance.make_request()
    
    user_make_request = User.add_request_id(From , to , request_id)
    
    json_verison = json_util.dumps(request_id)
    return make_response({'message':REQUEST_SENT_MESSAGE , "request": json_verison } , HTTP_201_CREATED)
    
def remove_friend():
    body = json.loads(request.data)
    request_id = body["request_id"]
    
    request_doc = request_collection.find_one({"_id": ObjectId(request_id)})
    
    if not request_doc:
        return make_response({'message':"No request with from current Id"} , HTTP_400_BAD_REQUEST)
    
    User.remove_request_id(request_doc['from'] , request_doc['to'] ,  ObjectId(request_id))
    request_collection.find_one_and_delete({ "_id":  ObjectId(request_id) })
    
    return make_response({'message':"request deleted successfully"} , HTTP_201_CREATED)
    