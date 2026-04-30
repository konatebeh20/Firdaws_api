from flask_restful import Resource
from flask import request
from helpers.admin import *


class AdminApi(Resource):
    def post(self, route):
        if route == "createadmin": 
            return CreateAdmin()

        if route == "getsingleadmin":
            return GetSingleAdmin()
        
        if route == "loginadmin":
            return LoginAdmin()

    def get(self, route):
        if route == "getalladmin":
            return GetAllAdmin()

    def patch(self, route):
        if route == "updateadmin":
            return UpdateAdmin()
        
    def delete(self, route):
        if route == "deleteadmin":
            return DeleteAdmin()
