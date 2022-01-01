# coding: utf-8
import datetime
import os
import pandas as pd
import random
import unittest

from czsc.utils import echarts_plot as plot
from czsc.analyze import CZSC,NewBar
from czsc.enum import Freq

cur_path = os.path.split(os.path.realpath(__file__))[0]

class Test_PLOT(unittest.TestCase) :
    def test_heat_map(self):
        data = [{"x": "{}hour".format(i), "y": "{}day".format(j), "heat": random.randint(0, 50)}
                for i in range(24) for j in range(7)]
        x_label = ["{}hour".format(i) for i in range(24)]
        y_label = ["{}day".format(i) for i in range(7)]
        hm = plot.heat_map(data, x_label=x_label, y_label=y_label)
        file_html = 'render.html'
        hm.render(file_html)
        assert os.path.exists(file_html)
        os.remove(file_html)


    def test_kline_pro(self):
        file_kline = os.path.join(cur_path, "data/000001.SH_D.csv")
        kline = pd.read_csv(file_kline, encoding="utf-8")
        bars = [NewBar(symbol=row['symbol'], id=i, freq=Freq.D, open=row['open'], dt=datetime.datetime.strptime(row['dt'], "%Y-%m-%d %H:%M:%S"),#"%Y/%m/%d %H:%M"),
                       close=row['close'], high=row['high'], low=row['low'], vol=row['vol'])
                for i, row in kline.iterrows()]
        ka = CZSC(bars)
        # ka.open_in_browser()
        file_html = 'czsc_render.html'
        chart = ka.to_echarts()
        chart.render(file_html)
        assert os.path.exists(file_html)
        os.remove(file_html)
