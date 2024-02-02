FROM viime/opencpu-base

COPY server.conf /etc/opencpu/

ADD viime /viime
RUN R -e 'library(devtools); library(roxygen2); install("viime", dependencies=NA, quiet=TRUE, upgrade="never")'

CMD service cron start && /usr/lib/rstudio-server/bin/rserver && apachectl -DFOREGROUND
