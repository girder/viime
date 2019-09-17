FROM metabulo/opencpu-base

ADD metabulo /metabulo
RUN R -e 'library(devtools); library(roxygen2); setwd("/metabulo"); devtools::update_packages(devtools::dev_package_deps()$package, dependencies=NA, quiet=TRUE, upgrade="never"); document();  setwd("/");install("metabulo", dependencies=NA, quiet=TRUE, upgrade="never")'

CMD service cron start && /usr/lib/rstudio-server/bin/rserver && apachectl -DFOREGROUND
