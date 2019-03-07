FROM metabulo/opencpu-base

ADD metabulo /metabulo
RUN R -e 'library(devtools); library(roxygen2); setwd("/metabulo"); document(); setwd("/"); install("metabulo")'

CMD service cron start && /usr/lib/rstudio-server/bin/rserver && apachectl -DFOREGROUND
