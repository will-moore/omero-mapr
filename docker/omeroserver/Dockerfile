FROM openmicroscopy/omero-ssh-daemon-c7:0.1.1
MAINTAINER A.Tarkowska@dundee.ac.uk

# OMERO prerequesties
RUN yum install -y epel-release \
    && yum clean all

RUN yum install -y wget unzip git \
    && yum clean all

RUN yum install -y zlib-devel \
    libjpeg-devel \
    libpng-devel \
    libtiff-devel \
    && yum clean all

# Install Java
RUN yum install -y java-1.8.0-openjdk-devel \
    && yum clean all

# Install Python and other dependences
RUN yum install -y \
    python-pip python-devel \
    numpy scipy \
    python-pillow \
    python-matplotlib python-tables \
    && yum clean all

# Install Ice 3.6
RUN cd /etc/yum.repos.d && wget https://zeroc.com/download/rpm/zeroc-ice-el7.repo
RUN yum install -y gcc gcc-c++ \
    libdb-utils \
    openssl-devel bzip2-devel expat-devel \
RUN cd /etc/yum.repos.d && yum install -y ice-all-runtime ice-all-devel
RUN pip install "zeroc-ice>3.5,<3.7"

# Install Postgres tools
RUN yum -y install http://yum.postgresql.org/9.5/redhat/rhel-7-x86_64/pgdg-centos95-9.5-2.noarch.rpm \
    && yum clean all
RUN yum -y install postgresql95 \
    && yum clean all

# RUN sript
ADD ./run.sh /tmp/run.sh
RUN chown omero:omero /tmp/run.sh
RUN chmod a+x /tmp/run.sh

# AS OMERO user
USER omero
ENV HOME /home/omero

WORKDIR $HOME

CMD ["/tmp/run.sh"]
