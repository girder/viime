FROM viime/opencpu-base

ADD viime /viime
RUN R -e 'library(devtools); library(roxygen2); setwd("/viime"); document(); setwd("/"); install("viime")'

CMD service cron start && /usr/lib/rstudio-server/bin/rserver && apachectl -DFOREGROUND
