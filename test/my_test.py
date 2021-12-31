# coding: utf-8
import os
import unittest
import datetime
import time

cur_path = os.path.split(os.path.realpath(__file__))[0]

class Test_My(unittest.TestCase) :
    def test_Caltime(self):
        date1 = datetime.datetime.strptime("2018/8/27 15:00", "%Y/%m/%d %H:%M")
        datem = datetime.datetime.strptime("2018/9/10 15:00", "%Y/%m/%d %H:%M")
        date2 = datetime.datetime.strptime("2018/9/4 15:00", "%Y/%m/%d %H:%M")

        print(date1 <= datem)
        print(datem <= date2)
