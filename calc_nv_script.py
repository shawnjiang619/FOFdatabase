#from jqdatasdk import *
#auth('18510437635','Happy123!')
# 用累计超额收益测算真实净值
import pandas as pd
import xlwt
import xlrd
from xlutils.copy import copy

downloaded_directory = 'C:/Users/zhangguanglei/fof/downloaded/'
formatted_directory= 'C:/Users/zhangguanglei/fof/formatted/'

if __name__ == '__main__':
    file_path = downloaded_directory + '华软新动力净值测算.xls'
    date_format = xlwt.XFStyle()
    date_format.num_format_str = 'yyyy/mm/dd'
    f = pd.ExcelFile(file_path)

    for i in f.sheet_names:
        rb = xlrd.open_workbook(file_path)
        wb = copy(rb)
        w_sheet = wb.get_sheet(0)

        df = pd.read_excel(file_path, sheet_name=i)
        print(df)

        #df_price = get_price('000905.XSHG', start_date='2017-09-20 00:00:00', end_date='2018-09-28 00:00:00', frequency='1d')
        k = 1
        CAR1 = df.loc[0].at['累计超额收益']
        CAR2 = df.loc[1].at['累计超额收益']
        index_nv1 =  df.loc[0].at['500净值']
        index_nv2 = df.loc[1].at['500净值']
        print(len(df.index))
        while k < len(df.index) - 1:
            rt = (CAR2-CAR1)/CAR1 + (index_nv2-index_nv1)/index_nv1
            w_sheet.write(k+1, 4, rt)
            print('wrote: ', df.loc[k+1].at['时间'])
            CAR1 = df.loc[k].at['累计超额收益']
            CAR2 = df.loc[k+1].at['累计超额收益']
            index_nv1 = df.loc[k].at['500净值']
            index_nv2 = df.loc[k+1].at['500净值']
            k+=1
            print("updated k = ", k)
        wb.save(file_path)

