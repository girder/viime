args = commandArgs(trailingOnly=TRUE)
if (length(args)==0) {
  stop("Have to provide the data file (input file).n", call.=FALSE)
} else if (length(args)==1) {
    data <- read.csv(file=args[1]);
    stripchart(data)
}
