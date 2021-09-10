import pandas as pd
from datetime import date
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy
from sqlalchemy.sql import exists
from ormModels import *
import shutil
import math


directory = 'C:/Users/zhangguanglei/fof/downloaded/'
file = '公募FOF回测用重点池子.xlsx'
file2 = '公募FOF回测用重点池子_净值.xls'

if __name__ == '__main__':
    file_path = directory + file
    df_info = pd.read_excel(file_path)

    file_path2 = directory + file2
    df_nv = pd.read_excel(file_path2)

    # 遍历得到每一支基金的info
    k=0
    while k < len(df_info.index):
        # 提取公基金相关信息,处理数据格式]
        fund_code = df_info.iloc[k, 0]
        fund_name = df_info.iloc[k, 1].encode('utf-8')
        fund_advisor = str(df_info.iloc[k, 3]).encode('utf-8')
        company_name = df_info.iloc[k, 7].encode('utf-8')
        update_date = date.today()
        # fund_type = data_frame.iloc[k, ].astype(int).item()
        # fund_size = data_frame.iloc[0, 7].item()
        k+=1
        # 初始化数据库连接:
        engine = create_engine('mysql+mysqlconnector://jtx:Happy@2021@localhost:3306/fof_public')
        # 创建DBSession类型:
        DBSession = sessionmaker(bind=engine)
        # 创建session对象:
        session = DBSession()

        # 初始化company_info.id
        comp_id = 0
        # 通过公司名判断该公司是否存在数据库
        if not session.query(exists().where(CompanyInfo.name == company_name)).scalar():
            # 如果该公司不存在表中，插入一条

            # 创建新company对象:
            new_company = CompanyInfo(name=company_name, fund_num=1)
            # 添加到session:
            session.add(new_company)
            print("added new company", company_name)
        elif not session.query(exists().where(FundInfo.name == fund_name)).scalar():
            # 该公司已存在表中，基金不存在表中，仅更新基金数(fund_num)
            print("company already exists", company_name)
            _ = session.query(CompanyInfo).filter(CompanyInfo.name == company_name) \
                .update({CompanyInfo.fund_num: CompanyInfo.fund_num + 1}, synchronize_session=False)
            print("updated company_info.fund_num: ", company_name)

            # 拿到company_info.id用作fund_info的foreign key
            temp_company = session.query(CompanyInfo).filter(CompanyInfo.name == company_name).one()
            comp_id = temp_company.id

        # 拿到company_info.id用作fund_info的foreign key
        temp_company = session.query(CompanyInfo).filter(CompanyInfo.name == company_name).one()
        comp_id = temp_company.id

        # 初始化fund_id
        fund_id = 0
        # 检查该基金是否已存在
        if not session.query(exists().where(FundInfo.name == fund_name)).scalar():
            # 插入一条到基金基本信息表
            new_fund = FundInfo(name=fund_name, company_id=comp_id, advisor=fund_advisor,
                                update_date=update_date)
            # 添加到session:
            session.add(new_fund)
            print("added new fund_info", fund_name)
            session.flush()
            # 拿到fund_info.id
            fund_id = new_fund.id
            # 插入一条到基金指标表
            new_fund_indicators = FundIndicator(fund_id=fund_id, trade_date=update_date)
            # 添加到session:
            session.add(new_fund_indicators)
            print("added new fund_indicators", fund_name)
        else:
            # 拿到fund_info.id用作fund_nv的foreign key
            temp_fund = session.query(FundInfo).filter(FundInfo.name == fund_name).one()
            fund_id = temp_fund.id

        # 插入基金净值信息
        for i in range(len(df_nv.index)):
            if not df_nv.loc[i].at["代码"] == fund_code:
                continue
            trade_d = df_nv.loc[i].at["trddt"]
            nv = df_nv.loc[i].at["NAV_ADJ"]

            if not session.query(
                    exists().where(FundNv.fund_id == fund_id).where(FundNv.trade_date == trade_d)).scalar():
                new_fund_nv = FundNv(fund_id=fund_id, trade_date=trade_d, net_value=nv,
                                     update_date=update_date)
                session.add(new_fund_nv)
                # print("added a nv query")

        # 提交即保存到数据库:
        session.commit()
        # 关闭session:
        session.close()
        print("finished processing, disconnecting sql")
