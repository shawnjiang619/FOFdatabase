# 首次批量导入净值信息

import pandas as pd
import xlwt
import math

downloaded_directory = 'C:/Users/zhangguanglei/fof/downloaded/'
formatted_directory= 'C:/Users/zhangguanglei/fof/formatted/'

if __name__ == '__main__':
    file_path = downloaded_directory + '潼骁产品净值数据_20210726.xlsx'
    date_format = xlwt.XFStyle()
    date_format.num_format_str = 'yyyy/mm/dd'
    f = pd.ExcelFile(file_path)
    for i in f.sheet_names:
        if i == 'Sheet1':
            continue
        df = pd.read_excel(file_path, sheet_name=i)

        """for col in df.columns:
        if col == "产品名称":
            continue"""
        #fund_name = df.loc[0].at['产品名称']
        workbook = xlwt.Workbook(encoding='utf-8')  # 新建工作簿
        sheet1 = workbook.add_sheet('sheet1')  # 新建sheet
        sheet1.write(0, 0, 'date')
        sheet1.write(0, 1, 'nv')
        sheet1.write(0, 2, 'anv')
        sheet1.write(0, 3, 'name' )
        sheet1.write(0, 4, '基金策略类别 1:指数增强 2:指数中性 3:灵活对冲 4:CTA 5:多策略 6:套利 7:主动多头')
        sheet1.write(0, 5, 'advisor')
        sheet1.write(0, 6, 'company')
        sheet1.write(0, 7, 'fund_size')
        fund_name = df.loc[0].at['产品名称']
        sheet1.write(1, 3, fund_name)

        """if 'cta' in i or 'CTA'in i:
            sheet1.write(1, 4, 4)
        elif '增强' in i:
            sheet1.write(1, 4, 1)
        elif '稳' in i:
            sheet1.write(1, 4, 2)"""


        sheet1.write(1, 5, '')
        sheet1.write(1, 6, '潼骁投资')
        #sheet1.write(1, 7, 260)
        nv = df.loc[0].at["单位净值"]


        anv = df.loc[0].at['累计净值']

        """if '估值日期' in df.columns:
            date = df.loc[0].at['估值日期']
        elif '净值日期' in df.columns:
            date = df.loc[0].at['净值日期']
        else:
            date = df.loc[0].at['产品名称']
        """
        #date = df.loc[0].at['净值日期']
        #date = pd.to_datetime(str(df.loc[0].at['净值日期']), format="%Y%d%m")
        date = pd.to_datetime(str(df.loc[0].at['净值日期']))
        print(date)
        k = 0
        w = 0
        while k < len(df.index):
            nv = df.loc[k].at["单位净值"]
            # df.loc[k].at['净值日期']
            date = pd.to_datetime(str(df.loc[k].at['净值日期']), format="%Y%m%d")
            anv = df.loc[k].at['累计净值']

            if not math.isnan(nv):
                print('writing: ', nv, anv, date)
                sheet1.write(w+1, 0, date, date_format)
                sheet1.write(w+1, 1, nv)
                sheet1.write(w+1, 2, anv)
                w+=1
            k += 1




        workbook.save(formatted_directory + "基金净值数据-" + fund_name + '.xlsx')  # 保存
        print("saved file: " + "基金净值数据-" + fund_name + '.xlsx')
