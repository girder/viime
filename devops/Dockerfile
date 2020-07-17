FROM viime/opencpu-base

ADD viime /viime
RUN R -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/mnormt/mnormt_1.5-6.tar.gz", repos=NULL, type="source")'
RUN R -e 'library(devtools); library(roxygen2); install("viime", dependencies=NA, quiet=TRUE, upgrade="never")'

CMD service cron start && /usr/lib/rstudio-server/bin/rserver && apachectl -DFOREGROUND
