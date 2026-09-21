CREATE DATABASE sentiment_analysis;
USE sentiment_analysis;


create table users(
id int auto_increment primary key,
username varchar(100),
email varchar(100),
password varchar(100)
);

create table reviews (
id int auto_increment primary key,
username varchar(100),
college varchar(100),
review text,
sentiment varchar(20),
created_at timestamp default current_timestamp
);

select * from users;
select * from reviews;

