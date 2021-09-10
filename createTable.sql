-- 基金公司的信息表
CREATE TABLE `company_info` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `name` varchar(100) NOT NULL COMMENT '基金公司名称',
  `fund_size` decimal COMMENT '基金管理规模(亿)',
  `fund_num` int(11) COMMENT '基金数',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 储存基金的相关信息，主键为id
-- 每一条数据通过外键company_id与company_info.id关联
CREATE TABLE `fund_info` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `name` varchar(100) NOT NULL COMMENT '基金名称',
  `company_id` int(10) unsigned DEFAULT NULL COMMENT '表外键,关联company_info.id',
  `type` int(11) COMMENT '基金策略类别 1：指数增强 2：指数中性 3：灵活对冲 4：CTA 5:多策略 6:套利 7:主动多头',
  `advisor` varchar(40) DEFAULT NULL COMMENT '负责投资顾问',
  `update_date` date DEFAULT NULL COMMENT '基金入库时间',
  PRIMARY KEY (`id`),
  KEY `company_id` (`company_id`),
  CONSTRAINT `fund_info_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `company_info` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 储存每只基金的时间序列数据
-- 每一条数据通过外键fund_id与fund_info.id关联
CREATE TABLE `fund_nv` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `fund_id` int(10) unsigned DEFAULT NULL COMMENT '表外键,关联fund_info.id',
  `trade_date` date DEFAULT NULL COMMENT '净值数据对应的历史时间',
  `net_value` float DEFAULT NULL COMMENT '基金单位净值',
  `accumulated_net_value` float DEFAULT NULL COMMENT '基金累计净值',
  `update_date` date DEFAULT NULL COMMENT '净值更新时间',
  PRIMARY KEY (`id`),
  KEY `fund_id` (`fund_id`),
  CONSTRAINT `fund_data_ibfk_1` FOREIGN KEY (`fund_id`) REFERENCES `fund_info` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 储存每只基金的计算指标，每天更新一次
-- 每一条数据通过外键fund_id与fund_info.id关联
CREATE TABLE `fund_indicators` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `fund_id` int(10) unsigned DEFAULT NULL COMMENT '表外键,关联fund_info.id',
  `trade_date` date DEFAULT NULL COMMENT '指标更新时间',
  `AAGR` float DEFAULT NULL COMMENT '年化收益率',
  `max_drawdown` float DEFAULT NULL COMMENT '最大回撤',
  `calmar_ratio` float DEFAULT NULL COMMENT 'Calmar比率',
  `sharpe_ratio` float DEFAULT NULL COMMENT '夏普比率',
  `var` float DEFAULT NULL COMMENT '方差',
  `sd` float DEFAULT NULL COMMENT '标准差',
  `semi_var` float DEFAULT NULL COMMENT '下偏方差',
  `semi_dev` float DEFAULT NULL COMMENT '半标准差',
  PRIMARY KEY (`id`),
  KEY `fund_id` (`fund_id`),
  CONSTRAINT `fund_indicators_ibfk_1` FOREIGN KEY (`fund_id`) REFERENCES `fund_info` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;