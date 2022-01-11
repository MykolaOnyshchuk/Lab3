import datetime
import threading
import multiprocessing as mp

from flask_restful import reqparse

from DB import SingletonDB
from ObjectBuilder import Director, Provider1ObjectBuilder, Provider2ObjectBuilder, OwnObjectBuilder
from psycopg2.extras import execute_values

class SingletonCache(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
class CacheProduct(metaclass=SingletonCache):
    def __init__(self):
        self.own_cache = []
        self.service_1_cache = []
        self.service_2_cache = []
    def time_to_update(self):
        dt = datetime.datetime.now()
        tomorrow = dt + datetime.timedelta(days=1)
        return (datetime.datetime.combine(tomorrow, datetime.time.min) - dt).seconds
    def own_prod(self, q):
        director = Director()
        builder = OwnObjectBuilder()
        director.builder = builder
        director.build_all_models()
        own = builder.model
        print(len(own.models))
        q.put(own.models)

    def serv1_prod(self, q):
        director = Director()
        builder = Provider1ObjectBuilder()
        director.builder = builder
        director.build_all_models()
        serv1 = builder.model
        print(len(serv1.models))
        q.put(serv1.models)
    def serv2_prod(self, q):
        director = Director()
        builder = Provider2ObjectBuilder()
        director.builder = builder
        director.build_all_models()
        serv2 = builder.model
        print(len(serv2.models))
        q.put(serv2.models)
    def update(self):
        conn = SingletonDB().conn
        q1 = mp.Queue()
        p1 = mp.Process(target=self.own_prod, args=(q1,))

        q2 = mp.Queue()
        p2 = mp.Process(target=self.serv1_prod, args=(q2,))

        q3 = mp.Queue()
        p3 = mp.Process(target=self.serv2_prod, args=(q3,))
        p1.start()
        p2.start()
        p3.start()
        self.own_cache = q1.get()
        self.service_1_cache = q2.get()
        self.service_2_cache = q3.get()
        for i in range(0, len(self.service_1_cache)):
            self.service_1_cache[i]["id"] += 150000
            self.service_2_cache[i]["id"] += 300000
        with conn.cursor() as cursor:
            cursor.execute('TRUNCATE "public.ModelCaching"')
            execute_values(cursor,
                           '''INSERT INTO "public.ModelCaching" ("id", "pageNumber", "xCoord", "yCoord", "width", "height", "price", "payment", "status", "chosenByUser") VALUES %s''', #('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')'''%(args["product_name"], args["desciption"], str(args["sale_type_id"]), str(args["start_date"]), str(args["end_date"]), str(args["delivery_type_id"]), str(args["delivery_price"]), str(args["delivery_time"]), str(args["price"]),  str(args["seller_id"])))
                            [(str(args["id"]), str(args["pageNumber"]), str(args["xCoord"]), str(args["yCoord"]), str(args["width"]),
                              str(args["height"]), str(args["price"]), str(args["payment"]), str(args["status"]),
                              str(args["chosenByUser"])) for args in self.own_cache + self.service_1_cache + self.service_2_cache])
        conn.commit()
        p1.join()
        p2.join()
        p3.join()
        timer = threading.Timer(self.time_to_update(), self.update)
        timer.start()
    def get_cache(self):
        parser = reqparse.RequestParser()
        parser.add_argument("pageNumberMin")
        parser.add_argument("pageNumberMax")
        parser.add_argument("payment")
        parser.add_argument("min_price")
        parser.add_argument("max_price")
        args = parser.parse_args()
        parse_str = '''SELECT * FROM "public.ModelCaching" '''
        filt_opt = []
        if args['pageNumberMin']:
            filt_opt.append(['"pageNumber">', args['pageNumberMin']])
        if args['pageNumberMax']:
            filt_opt.append(['"pageNumber"<', args['pageNumberMax']])
        if args['payment']:
            filt_opt.append(['"payment"=', args['payment']])
        if args['min_price']:
            filt_opt.append(['"price">', args['minPrice']])
        if args['max_price']:
            filt_opt.append(['"price"<', args['maxPrice']])
        if len(filt_opt)>0:
            parse_str += 'WHERE '
        for i in range(len(filt_opt)):
            parse_str += filt_opt[i][0]+"'" + filt_opt[i][1] + "'"
            if i+1 < len(filt_opt):
                parse_str += ' AND '
        conn = SingletonDB().conn
        with conn.cursor() as cursor:
            cursor.execute(parse_str)
            rows = cursor.fetchall()
        result = []
        for row in rows:
            a = {"id": row[0], "pageNumber": str(row[1]),
                 "xCoord": str(row[2]), "yCoord": row[3], "width": row[4],
                 "height": str(row[5]), "price": row[6], "payment": row[7], "status": row[8],
                 "chosenByUser": row[9]}
            result.append(a)
        print(result)
        return result