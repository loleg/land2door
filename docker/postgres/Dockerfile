FROM postgres:10

RUN pg_createcluster 10 blemmy

USER postgres

RUN /etc/init.d/postgresql start &&\
      psql --command "CREATE USER blemmy WITH SUPERUSER PASSWORD 'blemmy';" &&\
      createdb -O blemmy blemmy

USER root

COPY ./backup.sh /usr/local/bin/backup
RUN chmod +x /usr/local/bin/backup

COPY ./restore.sh /usr/local/bin/restore
RUN chmod +x /usr/local/bin/restore

COPY ./list-backups.sh /usr/local/bin/list-backups
RUN chmod +x /usr/local/bin/list-backups
