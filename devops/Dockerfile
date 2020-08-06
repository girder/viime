FROM viime/opencpu-base

ADD viime /viime
RUN R -e 'library(devtools); library(roxygen2); install("viime", dependencies=NA, quiet=TRUE, upgrade="never")'
RUN R -e 'install.packages("BiocManager"); BiocManager::install("mixOmics")'

CMD service cron start && /usr/lib/rstudio-server/bin/rserver && apachectl -DFOREGROUND
