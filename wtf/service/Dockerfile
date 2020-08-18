FROM ubuntu:12.04

ENV DEBIAN_FRONTEND=noninteractive 
RUN apt-get update && apt-get -yq install apache2 mysql-server libapache2-mod-php5 php5-mcrypt php5-mysql

CMD if [ ! -d /var/lib/mysql/mysql ] ; then dpkg-reconfigure mysql-server-5.5 ; fi ; service apache2 start ; exec mysqld
