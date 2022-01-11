from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Dict

from flask_restful import reqparse

from DB import SingletonDB
import requests
from SpecificationFilter import MinimalPageNumber, MaximalPageNumber, MaximalPrice, MinimalPrice, Payment


class ObjectBuilder(ABC):
    @property
    @abstractmethod
    def model(self) -> None:
        pass

    @abstractmethod
    def extract_from_source(self) -> None:
        pass

    @abstractmethod
    def reformat(self) -> None:
        pass

    @abstractmethod
    def filter(self) -> None:
        pass


class Provider1ObjectBuilder(ObjectBuilder):
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._model = OwnModel()

    @property
    def model(self) -> OwnModel:
        model = self._model
        self.reset()
        return model

    def extract_from_source(self) -> None:
        self._model.set(requests.get('http://127.0.0.1:5001/search/').json())

    def reformat(self) -> None:
        pass

    def filter(self) -> None:
        self._model.filter()


class Provider2ObjectBuilder(ObjectBuilder):
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._model = OwnModel()

    @property
    def model(self) -> OwnModel:
        model = self._model
        self.reset()
        return model

    def extract_from_source(self) -> None:
        #self._model.set(requests.get('http://127.0.0.1:5002/price-list/').json())
        page = [0]
        page_n = 1
        while len(page) > 0:
            page = requests.get('http://127.0.0.1:5002/price-list?page=' + str(page_n)).json()
            print(len(page))
            page_n += 1
            self._model.models += page

    def reformat(self) -> None:
        full_models = []
        print("reform")
        for row in self._model.models:
            full_models.append(requests.get('http://127.0.0.1:5002/details/'+str(row["id"])).json())
            #print(row["product_id"])
        self._model.set(full_models)

    def filter(self) -> None:
        self._model.filter()


class OwnObjectBuilder(ObjectBuilder):
    def __init__(self) -> None:
        self.reset()
        self.db = SingletonDB()

    def reset(self) -> None:
        self._model = OwnModel()

    @property
    def model(self) -> OwnModel:
        model = self._model
        self.reset()
        return model

    def extract_from_source(self) -> None:
        self._model.set(self._model.select_all_db_data())

    def reformat(self) -> None:
        my_list = []
        for row in self.model.models:
            a = {"id": row[0], "pageNumber": str(row[1]),
                 "xCoord": str(row[2]), "yCoord": row[3], "width": row[4],
                 "height": str(row[5]), "price": row[6], "payment": row[7], "status": row[8],
                 "chosenByUser": row[9]}
            my_list.append(a)
        self._model.set(my_list)

    def filter(self) -> None:
        self._model.filter()


class Director:
    def __init__(self) -> None:
        self._builder = None

    @property
    def builder(self) -> ObjectBuilder:
        return self._builder

    @builder.setter
    def builder(self, builder: ObjectBuilder) -> None:
        self._builder = builder

    def build_all_models(self) -> None:
        self.builder.extract_from_source()
        self.builder.reformat()

    def build_filtered_model(self) -> None:
        self.builder.extract_from_source()
        self.builder.reformat()
        self.builder.filter()


class OwnModel():
    def __init__(self):
        self.models = []
        self.filtered_models = []
        self.conn = SingletonDB().conn
        self.args = {}

    def add(self, model: Dict[str, Any]):
        self.models.append(model)

    def join(self, another_model):
        self.models += another_model.models

    def drop(self, id):
        del self.models[id]

    def set(self, models):
        self.models = models

    def select_all_db_data(self):
        rows = []
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT "public.ModelPlacing"."id", "public.ModelPlacing"."pageNumber", "public.ModelPlacing"."xCoord", "public.ModelPlacing"."yCoord", "public.ModelPlacing"."width", "public.ModelPlacing"."height", "public.ModelPlacing"."price", "public.ModelPlacing"."payment", "public.ModelPlacing"."status", "public.ModelPlacing"."chosenByUser" FROM "public.ModelPlacing"')
            rows = cursor.fetchall()
        return rows

    def insert(self, args):
        with self.conn.cursor() as cursor:
            print(args)
            cursor.execute('''INSERT INTO "public.ModelPlacing" ("modelId", "pageNumber", "xCoord", "yCoord", "width", "height", "price", "payment", "status", "chosenByUser") VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'%s',%s)'''%(str(args["modelId"]), str(args["pageNumber"]), str(args["xCoord"]), str(args["yCoord"]), str(args["width"]), str(args["height"]), str(args["price"]), str(args["payment"]), str(args["status"]), str(args["chosenByUser"])))
        self.conn.commit()

        with self.conn.cursor() as cursor:
            cursor.execute(
                '''SELECT "public.ModelPlacing"."id", "public.ModelPlacing"."pageNumber", "public.ModelPlacing"."xCoord", "public.ModelPlacing"."yCoord", "public.ModelPlacing"."width", "public.ModelPlacing"."height", "public.ModelPlacing"."price", "public.ModelPlacing"."payment", "public.ModelPlacing"."status", "public.ModelPlacing"."chosenByUser" FROM "public.ModelPlacing" WHERE "public.id"='%s' ''' %
                args["id"])
            rows = cursor.fetchall()
        args = self.reform(rows[-1])
        with self.conn.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO "public.ModelCaching" ("id", "pageNumber", "xCoord", "yCoord", "width", "height", "price", "payment", "status", "chosenByUser") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'%s',%s)''' %
                (str(args["id"]), str(args["pageNumber"]),
                 str(args["xCoord"]), str(args["yCoord"]), str(args["width"]),
                 str(args["height"]), str(args["price"]), str(args["payment"]), str(args["status"]),
                 str(args["chosenByUser"])))
        self.conn.commit()

    def delete(self, id):
        with self.conn.cursor() as cursor:
            cursor.execute('DELETE FROM "public.ModelPlacing" WHERE "id"='+str(id))
            cursor.execute('DELETE FROM "public.ModelCaching" WHERE "id"=' + str(id))
        self.conn.commit()

    def update(self, args):
        query_str = 'UPDATE "public.ModelPlacing" SET '
        for key, value in args.items():
            if key != 'id' and value is not None:
                query_str += '"' + key + '"=' + "'" + str(value) + "',"
        query_str = query_str[0:-1]
        query_str += ' WHERE "id"=' + str(args["id"])
        with self.conn.cursor() as cursor:
            cursor.execute(query_str)
        self.conn.commit()

        with self.conn.cursor() as cursor:
            cursor.execute(
                '''SELECT "public.ModelPlacing"."id", "public.ModelPlacing"."pageNumber", "public.ModelPlacing"."xCoord", "public.ModelPlacing"."yCoord", "public.ModelPlacing"."width", "public.ModelPlacing"."height", "public.ModelPlacing"."price", "public.ModelPlacing"."payment", "public.ModelPlacing"."status", "public.ModelPlacing"."chosenByUser" FROM "public.ModelPlacing" WHERE "public.id"='%s' ''' %
                args["id"])
            rows = cursor.fetchall()
        args = self.reform(rows[-1])

        query_str = 'UPDATE CacheTable SET '
        for key, value in args.items():
            if key != 'product_id' and value != None:
                query_str += '"' + key + '"=' + "'" + str(value) + "',"
        query_str = query_str[0:-1]
        query_str += ' WHERE ""."id"=' + str(args["id"])
        with self.conn.cursor() as cursor:
            cursor.execute(query_str)
        self.conn.commit()


    def mfilter(self, x):
        #print(len(self.filtered_products))
        product_filter = MinimalPageNumber() & MaximalPageNumber() & MaximalPrice() & MinimalPrice() & Payment()
        if product_filter.is_satisfied_by(x, self.args):
            return x
        return None
            #self.filtered_products.append(x)


    def filter(self):
        # model_filter = MinimalPageNumber() & MaximalPageNumber() & MaximalPrice() & MinimalPrice() & Payment()
        models = []
        parser = reqparse.RequestParser()
        parser.add_argument("pageNumberMin")
        parser.add_argument("pageNumberMax")
        parser.add_argument("payment")
        parser.add_argument("minPrice")
        parser.add_argument("maxPrice")
        self.args = parser.parse_args()
        import multiprocessing
        self.conn = None
        t1 = time.time()
        with multiprocessing.Pool(4) as pool:
            self.models = pool.map(self.mfilter, self.models)
        print(time.time()-t1)
        t1 = time.time()
        self.models = list(filter(None, self.models))
        print(time.time() - t1)
        self.conn = SingletonDB().conn

    def reform(self, row):
        return {"id": row[0], "pageNumber": str(row[1]),
                 "xCoord": str(row[2]), "yCoord": row[3], "width": row[4],
                 "height": str(row[5]), "price": row[6], "payment": row[7], "status": row[8],
                 "chosenByUser": row[9]}