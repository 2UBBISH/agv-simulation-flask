import traceback
# from src.drivers.mysql import m

class Service():
    def __init__(self):
        pass

    # def dcInfo(self, theDate):
    #     result = None
    #     try:
    #         sql = "select name from cb_order where status = 1 and order_time = '%s'" % (
    #             theDate)
    #         print(sql)
    #         with m.pool() as conn:
    #             result = conn.fetch_all(sql)
    #     except Exception as ex:
    #         traceback.print_exc()
    #     finally:
    #         pass
    #
    #     orderCount = 0
    #     order = []
    #
    #     if result is not None:
    #         orderCount = len(result)
    #         order = list(map(lambda item: item["name"], result))
    #
    #     return order, orderCount
    #
    # ###################
    # # 判断是否已经点过餐
    # ###################
    # def hasDc(self, username, theDate):
    #     result = None
    #     try:
    #         sql = "select name from cb_order where status = 1 and order_time = '%s' and `name` = '%s'" % (
    #             theDate, username)
    #         print(sql)
    #         with m.pool() as conn:
    #             result = conn.fetch_all(sql)
    #     except Exception as ex:
    #         traceback.print_exc()
    #     finally:
    #         pass
    #
    #     if result is not None and len(result) > 0:
    #         return True
    #     else:
    #         return False
    #
    # ###################
    # # 插入点餐表
    # ###################
    # def dc(self, username, theDate):
    #     try:
    #         sql = "insert into cb_order (order_time, status, name )values ('%s', 1, '%s');" % (theDate, username)
    #         print(sql)
    #         with m.pool() as conn:
    #             conn.insert(sql)
    #     except Exception as ex:
    #         traceback.print_exc()
    #     finally:
    #         pass


