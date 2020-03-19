create schema if not exists testtable;

use testtable;

drop table if exists testtable;
create table if not exists testtable (
  Email varchar(100) not null unique,
  Username varchar(100) not null unique,
  Password varchar(300) not null,
  primary key (Username)
);

drop table if exists photos;
create table if not exists photos(
  Username varchar(100) not null,
  PhotoURL varchar(300) not null,
  primary key (PhotoURL)
);

drop table if exists autoscalingconfig;
create table if not exists autoscalingconfig (
  ascid bigint(32) not null auto_increment,
  cpu_grow float not null,
  cpu_shrink float not null,
  ratio_expand float not null,
  ratio_shrink float not null,
  timestamp datetime not null,
  primary key (ascid)
)AUTO_INCREMENT=200 DEFAULT CHARSET=utf8;

drop table if exists requestperminute;
create table if not exists requestperminute (
  requestid bigint(32) not null auto_increment,
  instance_id varchar(50) not null,
  timestamp DATETIME not null,
  primary key (requestid)
)DEFAULT CHARSET=utf8;

