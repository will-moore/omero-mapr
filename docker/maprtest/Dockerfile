FROM openmicroscopy/omero-ssh-daemon-c7:0.1.1
MAINTAINER A.Tarkowska@dundee.ac.uk

RUN yum install -y epel-release \
    && yum clean all

RUN yum install -y git \
    && yum clean all

RUN yum install -y \
    python-pip python-devel \
    && yum clean all

RUN yum install -y libdb-utils \
    openssl-devel bzip2-devel expat-devel \
    && yum clean all

RUN yum install -y gcc gcc-c++ \
    zlib-devel \
    libjpeg-devel \
    libpng-devel \
    libtiff-devel \
    && yum clean all

RUN pip install virtualenv

# AS OMERO user
USER omero
ENV HOME /home/omero

WORKDIR $HOME
