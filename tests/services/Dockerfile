FROM ubuntu:22.04
LABEL description="Bugzilla image for testing purposes"
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ="Etc/UTC"
RUN apt update && \
    apt install --no-install-recommends -q -y \
    tzdata wget apache2 libcgi-pm-perl libdatetime-perl libdatetime-timezone-perl libdbi-perl \
    libdbix-connector-perl libdigest-sha-perl libemail-address-perl libemail-mime-perl \
    libemail-sender-perl libjson-xs-perl liblist-moreutils-perl libmath-random-isaac-perl \
    libtemplate-perl libtimedate-perl liburi-perl libmariadb-dev-compat libdbd-mysql-perl \
    libxmlrpc-lite-perl libsoap-lite-perl libapache2-mod-perl2 libtest-taint-perl \
    libjson-rpc-perl && \
    apt clean
RUN mkdir -p /var/www/webapps && \
    wget https://ftp.mozilla.org/pub/mozilla.org/webtools/bugzilla-5.0.6.tar.gz \
        -O /tmp/bugzilla-5.0.6.tar.gz&& \
    tar xvzf /tmp/bugzilla-5.0.6.tar.gz && \
    rm /tmp/bugzilla-5.0.6.tar.gz && \
    mv /bugzilla-5.0.6/ /var/www/webapps/bugzilla/ && \
    mkdir /var/www/webapps/bugzilla/data/
COPY bugzilla.conf /etc/apache2/sites-available/
COPY localconfig /var/www/webapps/bugzilla/
COPY params.json /var/www/webapps/bugzilla/data/
RUN a2dissite 000-default && \
    a2ensite bugzilla && \
    a2enmod cgi headers expires rewrite perl && \
    /var/www/webapps/bugzilla/checksetup.pl
CMD apachectl -D FOREGROUND
