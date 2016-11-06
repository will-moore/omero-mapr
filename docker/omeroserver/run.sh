#!/bin/bash

set -eux

sudo pip install omego

(cd /tmp && omego download --ice 3.6 --branch OMERO-DEV-merge-build server)

ZIP=$(ls /tmp/OMERO.server*.zip)
DIST=${ZIP%.zip}
rm -f $ZIP
mv $DIST ${HOME}/OMERO.server

until psql -h $OMERO_DB_HOST -p $OMERO_DB_PORT -U $OMERO_DB_USER -c '\l'; do
  >&2 echo "$OMERO_DB_HOST is unavailable - sleeping"
  sleep 5
done

>&2 echo "$OMERO_DB_HOST now accepts connections, creating database $OMERO_DB_NAME..."

echo "Loading config..."
${HOME}/OMERO.server/bin/omero config set omero.db.host $OMERO_DB_HOST
${HOME}/OMERO.server/bin/omero config set omero.db.port $OMERO_DB_PORT
${HOME}/OMERO.server/bin/omero config set omero.db.user $OMERO_DB_USER
${HOME}/OMERO.server/bin/omero config set omero.db.name $OMERO_DB_NAME
${HOME}/OMERO.server/bin/omero config set omero.data.dir "${HOME}/data"
mkdir -p ${HOME}/data

# initialize or upgarde the db
if psql -h $OMERO_DB_HOST -p $OMERO_DB_PORT -U $OMERO_DB_USER -lqt | cut -d \| -f 1 | grep -qw $OMERO_DB_NAME; then
    echo "WARNING: $OMERO_DB_NAME exists."
else
    createdb -h $OMERO_DB_HOST -p $OMERO_DB_PORT -U $OMERO_DB_USER $OMERO_DB_NAME
    echo "INFO: $OMERO_DB_NAME was created."
fi
omego db upgrade --serverdir ${HOME}/OMERO.server --dbname $OMERO_DB_NAME || omego db init --serverdir ${HOME}/OMERO.server --dbname $OMERO_DB_NAME

echo "Starting OMERO.server..."
${HOME}/OMERO.server/bin/omero admin start --foreground
