# FOF Database 

[TOC]

## intro

This repo stores the scripts to collect, clean, and analyze daily net value data of a bucket of private funds. 

These funds are potential targets to a actively managed fund of funds portfolio

## environment

### server

windows server 2016 datacenter

### database

Mysql


### scripting language

python

## database structure

fof consists 6 tables: company_info, fund_info, fund_nv, fund_indicators, index_info, index_nv

fof_public consists 4 tables: ompany_info, fund_info, fund_nv, fund_indicators

### table 1：company_info

stores fund company information

| field                   | type         | comment           |
| ------------------------ | ------------ | ---------------- |
| `company_info.id`        | int(10)      | primary id           |
| `company_info.name`      | varchar(100) | company name       |
| `company_info.fund_size` | DECIMAL      | capital under management() |
| `company_info.fund_num`  | int(11)      |number of funds    |

### table 2：fund_info

stores information of specific fund
each entry relates to company_info.id through foreign key company_id

| field                   | type         | comment           |
| ----------------------- | ------------ | ------------------------------------------------------------ |
| `fund_info.id`          | int(10)      | primary id                                                         |
| `fund_info.name`        | varchar(100) | fund name                                                    |
| `fund_info.company_id`  | int(10)      | foreign key,relates to company_info.id                                   |
| `fund_info.type`        | int(11)      | fund strategy 1:index_enhanced 2：index neutral 3：Flexible hedge 4：future 5:Multi-strategy  6:arbitrage 7:Active long |
| `fund_info.advisor`     | varchar(40)  | fund advisor                                                |
| `fund_info.update_date` | date         | fund update date                                                 |

### table 3：fund_nv

stores time series of each fund
each entry relates to fund_info.id through foreign key fund_id


| field                   | type         | comment                   |
| ------------------------------- | ------- | ----------------------- |
| `fund_nv.id`                    | int(10) | primary id                  |
| `fund_nv.fund_id`               | int(10) | foreign key,relates to fund_info.id |
| `fund_nv.trade_date`            | date    | time series timestamp  |
| `fund_nv.net_value`             | float   | fund net value            |
| `fund_nv.accumulated_net_value` | float   | fund accumulated_net_value       |
| `fund_nv.update_date`           | date    | update time           |

### 表四：fund_indicators
stores indicators of each fund, update daily
each entry relates to fund_info.id through foreign key fund_id

| field                   | type         | comment                    |
| ------------------------------ | ------- | ----------------------- |
| `fund_indicators.id`           | int(10) | primary id                  |
| `fund_indicators.fund_id`      | int(10) | foreign key,relates to fund_info.id |
| `fund_indicators.trade_date`   | date    | indicators update time            |
| `fund_indicators.AAGR`         | float   | Average Annual Growth Rate              |
| `fund_indicators.max_drawdown` | float   | max drawdown                |
| `fund_indicators.calmar_ratio` | float   | Calmar ratio              |
| `fund_indicators.sharpe_ratio` | float   | sharpe ratio                |
| `fund_indicators.var`          | float   | variance                    |
| `fund_indicators.sd`           | float   | standard deviation                  |
| `fund_indicators.semi_var`     | float   | semi variance                |
| `fund_indicators.semi_dev`     | float   | semi deviation                |

### table 5：index_info

Store information about representative index 
| field                  | type         | comment                                     |
| ----------------------- | ------------ | ---------------------------------------- |
| `index_info.id`         | int(10)      | primary id                                   |
| `index_info.name`       | varchar(100) | index name                                 |
| `index_info.type`       | int(11)      | index type 1：stock 2：bond 3：commdity 4：international |
| `fund_info.update_date` | date         | index update date                             |

index includes:

{'000300.XSHG':'Shanghai and Shenzhen 300',
 '000905.XSHG':'CSG 500',
 '000001.XSHG':'Shanghai Composite Index',
 '000016.XSHG':'Shanghai Securities 50',
 '399006.XSHE':'GEM Index',
 '399106.XSHE':'Shenzhen Stock Exchange Index',
 '000012.XSHG':'National Bond Index',
 '000022.XSHG':'Shanghai Stock Exchange Bond Index',
 'T8888.CCFX': '10-year Treasury Bond Contract',
 'TF8888.CCFX': '5-year government bond contract',
 'RB8888.XSGE':'Rebar Index',
 'M8888.XDCE':'Soybean Meal Index',
 'CL':'NYMEX Crude Oil',
 'GC':'COMEX Gold',
 'AHD':'LME aluminum 3 months'}

### table 6：index_nv
stores time series of each fund
each entry relates to index_info.id through foreign key fund_id

| field                  | type         | comment                    |
| :-------------------- | ------- | ----------------------- |
| `index_nv.id`         | int(10) | primary id                  |
| `index_nv.index_id`   | int(10) | foreign key,relates fund_info.id |
| `index_nv.trade_date` | date    | time series timestamp  |
| `index_nv.net_value`  | float   | index net value           |
| `fund_nv.update_date` | date    | update time            |



fof_public stores publicly traded funds, table structure is identitcal to fof


## Fund net value data handling process

1. download attachment 
   

2. insert to database 
   

template:

   templete_rongxi = {**'file_name'**: **'**comanyfile**'**, #File name
          **'fund_id'**: [695],
          **'date'**: **'Net Worth Date'**,
          **'nv'**: **'Unit Net Value'**,
          **'anv'**: **'Cumulative unit net value'**,

   ​ **'header'**: **0**}							  			   
   

3. calculate financial indicators



## script tools

- fund_combination_tester:

  Calculate the net value and derivative indicators of a given fund portfolio, support reading from the database and reading from local files

calculate the nv and financial indicators from specified portfolio

- update_index_script:



## run script in backgrounf



View the running script:

1. Windows find the command line:

2. The default path is C:\Users\zhangguanglei, enter command cd fof to enter the fof folder

3. Enter tasklist | findstr "python" to find the running process with python keywords


Run new script:

1. Enter pythonw file_name.py> file_name.log

   The remote server needs to add> file_name.log to ensure that it can be discovered by cmd, and the local only needs to enter pythonw file_name.py (very magical, I didn’t find the principle behind it)

2. Enter tasklist again | findstr "python" to find the newly running script process


End running script:

1. Enter taskkill /f /im process_id to end the script corresponding to process_id

Modify script running time/frequency:

1. Modify/add triggers in the python file after the cmd ends the script

2. Re-run the script after modification

apscheduler library documentation: https://apscheduler.readthedocs.io/en/stable/userguide.html#

Apscheduler library tutorial: https://zhuanlan.zhihu.com/p/144506204



Process information:

`fetchAttachment.py` background process id: 11300

`update_nv_script.py` background process id: 12896

`handleFiles.py` background process id: 12732

`update_index_script.py` background process id: 4336

`calculateIndicators.py` background process id: 12676

## Follow-up plan

Add a rate structure field to the table

Complete missing type information








