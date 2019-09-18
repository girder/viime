FROM viime/opencpu-base

ADD viime /viime
RUN R -e 'library(devtools); library(roxygen2); setwd("/viime"); devtools::update_packages(devtools::dev_package_deps()$package, dependencies=NA, quiet=TRUE, upgrade="never"); document(); setwd("/");install("viime", dependencies=NA, quiet=TRUE, upgrade="never")'

CMD service cron start && /usr/lib/rstudio-server/bin/rserver && apachectl -DFOREGROUND
