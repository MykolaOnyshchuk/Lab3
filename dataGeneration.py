import random
import psycopg2

def random_gen(id):
    modelId = random.randint(1, 4)
    pageNumber = random.randint(0, 300)
    xCoord = random.randint(0, 500)
    yCoord = random.randint(0, 1000)
    width = random.randint(0, 500)
    height = width // 2
    modelPlacingId = id
    price = random.randint(1000, 5000)
    payment = False
    chosenByUser = False
    randomBool = random.randint(0, 1)
    if randomBool == 0:
        chosenByUser = False
    else:
        chosenByUser = True
    if chosenByUser == True:
        randomBool = random.randint(0, 1)
        if randomBool == 0:
            payment = False
        else:
            payment = True
    statusPart1 = "Not accepted"
    if chosenByUser == True:
        statusPart1 = "Accepted"
    statusPart2 = "not paid"
    if payment == True:
        statusPart2 = "paid"
    status = statusPart1 + " and " + statusPart2
    return {
        "modelId": modelId, "pageNumber": pageNumber, "xCoord": xCoord, "yCoord": yCoord, "width": width, "height": height, "modelPlacingId": modelPlacingId, "price": price, "payment": payment,
        "status": status, "chosenByUser": chosenByUser

    }

def select_filtered_values1():
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='06012002', host='localhost')
    rows = []
    for i in range(0, 100000):
        args = random_gen(i + 1)
        with conn.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO "public.ModelPlacing" ("modelId", "pageNumber", "xCoord", "yCoord", "width", "height", "price", "payment", "status", "chosenByUser") VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'%s',%s)''' % (
                    str(args["modelId"]), str(args["pageNumber"]), str(args["xCoord"]), str(args["yCoord"]),
                    str(args["width"]), str(args["height"]), str(args["price"]), str(args["payment"]),
                    str(args["status"]),
                    str(args["chosenByUser"])))
    conn.commit()
    conn.close()
            #rows = cursor.fetchall()
    #return rows

def select_filtered_values2():
    conn = psycopg2.connect(dbname='architecture2', user='postgres', password='06012002', host='localhost')
    rows = []
    price_arr = []
    for i in range(0, 50000):
        args = random_gen(i + 1)
        with conn.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO "architecture2"."ModelPlacing" ("pageNumber", "xCoord", "yCoord", "width", "height", "status", "chosenByUser") VALUES(%s,%s,%s,%s,%s,'%s',%s)''' % (
                    str(args["pageNumber"]), str(args["xCoord"]), str(args["yCoord"]),
                    str(args["width"]), str(args["height"]), str(args["status"]), str(args["chosenByUser"])))

        price_arr.append({"model_placing_id": str(i + 1), "price": str(args["price"]), "payment": str(args["payment"])})

    conn.commit()
    conn.close()

    conn = psycopg2.connect(dbname='architecture2', user='postgres', password='06012002', host='localhost')
    for i in range(0, 50000):
        with conn.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO "architecture2"."ModelPlacingPayment" ("model_placing_id", "price", "payment") VALUES(%s,%s,%s)''' % (
                    str(i + 1), str(price_arr[i]["price"]), str(price_arr[i]["payment"])))

    conn.commit()
    conn.close()



if __name__ == "__main__":
    select_filtered_values1()
    select_filtered_values2()
