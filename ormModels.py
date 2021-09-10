# coding: utf-8
# stores sql orm class
from sqlalchemy import Column, DECIMAL, Date, Float, ForeignKey, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class CompanyInfo(Base):
    __tablename__ = 'company_info'

    id = Column(INTEGER(10), primary_key=True, comment='主键id')
    name = Column(String(100), nullable=False, comment='基金公司名称')
    fund_size = Column(DECIMAL(10, 0), comment='基金管理规模(亿)')
    fund_num = Column(INTEGER(11), comment='基金数')


class FundInfo(Base):
    __tablename__ = 'fund_info'

    id = Column(INTEGER(10), primary_key=True, comment='主键id')
    name = Column(String(100), nullable=False, comment='基金名称')
    company_id = Column(ForeignKey('company_info.id', ondelete='CASCADE'), index=True, comment='表外键,关联company_info.id')
    type = Column(INTEGER(11), comment='基金策略类别 1：指数增强 2：指数中性 3：灵活对冲 4：商品截面 5多策略')
    advisor = Column(String(40), comment='负责投资顾问')
    update_date = Column(Date, comment='基金入库时间')

    company = relationship('CompanyInfo')


class FundIndicator(Base):
    __tablename__ = 'fund_indicators'

    id = Column(INTEGER(10), primary_key=True, comment='主键id')
    fund_id = Column(ForeignKey('fund_info.id', ondelete='CASCADE'), index=True, comment='表外键,关联fund_info.id')
    trade_date = Column(Date, comment='指标更新时间')
    AAGR = Column(Float, comment='年化收益率')
    max_drawdown = Column(Float, comment='最大回撤')
    calmar_ratio = Column(Float, comment='Calmar比率')
    sharpe_ratio = Column(Float, comment='夏普比率')
    var = Column(Float, comment='方差')
    sd = Column(Float, comment='标准差')
    semi_var = Column(Float, comment='下偏方差')
    semi_dev = Column(Float, comment='半标准差')

    fund = relationship('FundInfo')


class FundNv(Base):
    __tablename__ = 'fund_nv'

    id = Column(INTEGER(10), primary_key=True, comment='主键id')
    fund_id = Column(ForeignKey('fund_info.id', ondelete='CASCADE'), index=True, comment='表外键,关联fund_info.id')
    trade_date = Column(Date, comment='净值数据对应的历史时间')
    net_value = Column(Float, comment='基金单位净值')
    accumulated_net_value = Column(Float, comment='基金累计净值')
    update_date = Column(Date, comment='净值更新时间')

    fund = relationship('FundInfo')

class IndexInfo(Base):
    __tablename__ = 'index_info'

    id = Column(INTEGER(10), primary_key=True, comment='主键id')
    name = Column(String(100), nullable=False, comment='指数名称')
    type = Column(INTEGER(11), comment='指数类别 1：股市 2：债市 3：商品 4：外围')
    update_date = Column(Date, comment='指数入库时间')

class IndexNv(Base):
    __tablename__ = 'index_nv'

    id = Column(INTEGER(10), primary_key=True, comment='主键id')
    index_id = Column(ForeignKey('index_info.id', ondelete='CASCADE'), index=True, comment='表外键,关联index_info.id')
    trade_date = Column(Date, comment='净值数据对应的历史时间')
    net_value = Column(Float, comment='指数净值')
    update_date = Column(Date, comment='净值更新时间')

    index = relationship('IndexInfo')