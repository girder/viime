# This script carries out a simple normalization based on sample weights/volumes
# this will require the indentification of a column of data containing sample/weights/volumes.
# In the example, a new dataframe was generated with a column called Weight


rm(list=ls())
# set the working directory
setwd("C:/Users/thoconne.ADS/Documents Backup - 102518/Avin/Kidney Disease Study/Human CKD/MMB Serum")

# --- generate a set of random weights for the samples

weights <- runif(33, min =80, max = 120) # this would normally be assigned during data import

mmb.serum.dat <- read.csv("MMB_serum.csv")
mmb.serum.meta <- mmb.serum.dat[,1:4]
mmb.serum.mat <- as.matrix(mmb.serum.dat[,5:191]); rownames(mmb.serum.mat) <- mmb.serum.dat[,1]

# generate data frame for sum & normalization factors
norm <- data.frame(x = numeric(33), y = numeric(33))
norm[,1] <- weights
rownames(norm) <- mmb.serum.dat[,1]
colnames(norm) <- c("weights, weightfactor")

# generate the normalization factor so that the sum of all metabolites for each sample is 100 mgs
norm[,2] <- 100/(norm[,1])

# apply the normalization to the original matrix dataset 

mmb.serum.mat.norm <- mmb.serum.mat*norm[,2]



