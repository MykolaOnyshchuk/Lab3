from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from ObjectBuilder import Director, OwnObjectBuilder, Provider1ObjectBuilder, Provider2ObjectBuilder, OwnModel
from DB import SingletonDB
from CacheProducts import CacheProduct


class Facade:
    def __init__(self):
        self.director = Director()
        self.parser = reqparse.RequestParser()
        self.empty_model = OwnModel()
        self.cache = CacheProduct()

    def get_prod(self):
        return self.cache.get_cache()

    def insert(self):
        self.parser.add_argument("modelId")
        self.parser.add_argument("pageNumber")
        self.parser.add_argument("xCoord")
        self.parser.add_argument("yCoord")
        self.parser.add_argument("width")
        self.parser.add_argument("height")
        self.parser.add_argument("price")
        self.parser.add_argument("payment")
        self.parser.add_argument("status")
        self.parser.add_argument("chosenByUser")

        args = self.parser.parse_args()
        self.empty_model.insert(args)

    def delete(self):
        self.parser.add_argument("id")
        args = self.parser.parse_args()
        self.empty_model.delete(args["id"])

    def update(self):
        self.parser.add_argument("id")
        self.parser.add_argument("modelId")
        self.parser.add_argument("pageNumber")
        self.parser.add_argument("xCoord")
        self.parser.add_argument("yCoord")
        self.parser.add_argument("width")
        self.parser.add_argument("height")
        self.parser.add_argument("model_placing_id")
        self.parser.add_argument("price")
        self.parser.add_argument("payment")
        self.parser.add_argument("status")
        self.parser.add_argument("chosenByUser")

        args = self.parser.parse_args()
        self.empty_model.update(args)
