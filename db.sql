-- user configuration
--init mysqld configure, 'mysqld --initialize', a default passwd is given.
--change passwd with 'mysqladmin' or the mysql benchmark
--connect with root and create new user and grant privileges:
--CREATE USER 'user'@'localhost' IDENTIFIED BY 'password';
--GRANT ALL PRIVILEGES ON *.* TO 'user'@'localhost';
--drop user: drop user 'username'

-- create database
CREATE DATABASE `ece1779` /*!40100 DEFAULT CHARACTER SET utf8 */;

-- create table
CREATE TABLE `user` (
  `userid` bigint(32) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(128) NOT NULL,
  `salt` varchar(64) NOT NULL,
  PRIMARY KEY (`userid`),
  UNIQUE KEY `username_UNIQUE` (`username`),
  UNIQUE KEY `password_UNIQUE` (`password_hash`),
  UNIQUE KEY `userid_UNIQUE` (`userid`),
  UNIQUE KEY `salt_UNIQUE` (`salt`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8;

CREATE TABLE `image` (
  `imageid` bigint(32) NOT NULL AUTO_INCREMENT,
  `path` varchar(140) NOT NULL,
  `userid` bigint(32) NOT NULL,
  PRIMARY KEY (`imageid`),
  KEY `userid_idx` (`userid`),
  CONSTRAINT `userid` FOREIGN KEY (`userid`) REFERENCES `user` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8;

-- connect RDS: mysql -h [endpoint] -P 3306 -u [username] -p

