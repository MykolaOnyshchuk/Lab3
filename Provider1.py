import random
import time

from flask import Flask
from flask_restful import Resource, Api, reqparse
import psycopg2
import copy
from SpecificationFilter import MinimalPageNumber, MaximalPageNumber, MaximalPrice, MinimalPrice, Payment


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonDB(metaclass=SingletonMeta):
    def __init__(self):
        self.conn = psycopg2.connect(dbname='architecture1', user='postgres', password='06012002', host='localhost')

    def select_filtered_values(self):
        rows = []
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT "architecture1"."ModelPlacing"."id", "architecture1"."ModelPlacing"."pageNumber", "architecture1"."ModelPlacing"."xCoord", "architecture1"."ModelPlacing"."yCoord", "architecture1"."ModelPlacing"."width", "architecture1"."ModelPlacing"."height", "architecture1"."ModelPlacing"."price", "architecture1"."ModelPlacing"."payment", "architecture1"."ModelPlacing"."status", "architecture1"."ModelPlacing"."chosenByUser" FROM "architecture1"."ModelPlacing"')
            rows = cursor.fetchall()
        return rows


class Models(Resource):
    #parser = reqparse.RequestParser()
    def get(self):
        db = SingletonDB()
        time.sleep(25)
        all_products = db.select_filtered_values()
        my_list = []
        for row in all_products:
            a = {"id": row[0], "pageNumber": row[1], "xCoord": row[2], "yCoord": str(row[3]), "width": str(row[4]), "height": row[5], "price": row[6], "payment": str(row[7]), "status": row[8], "chosenByUser": str(row[9])}
            my_list.append(a)
        all_products.clear()

        product_filter = MinimalPageNumber() & MaximalPageNumber() & MaximalPrice() & MinimalPrice() & Payment()
        products = []
        parser = reqparse.RequestParser()
        parser.add_argument("pageNumberMin")
        parser.add_argument("pageNumberMax")
        parser.add_argument("payment")
        parser.add_argument("minPrice")
        parser.add_argument("maxPrice")
        args = parser.parse_args()
        print(args)
        for i in my_list:
            #print(i)
            if product_filter.filtering_value_is_satisfied(i, args):
                products.append(i)
        return products


if __name__ == "__main__":
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Models, '/search/')
    app.run(port=5001, debug=True)
