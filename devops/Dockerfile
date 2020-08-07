FROM viime/opencpu-base

ADD viime /viime
RUN R -e 'BiocManager::install("mixOmics")'
RUN R -e 'library(devtools); library(roxygen2); install("viime", dependencies=NA, quiet=TRUE, upgrade="never")'

CMD service cron start && /usr/lib/rstudio-server/bin/rserver && apachectl -DFOREGROUND
