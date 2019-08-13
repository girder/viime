# This script carries out a  normalization based on a single sample.  The total metabolite concentrations
# of all samples will be scaled to match that of the reference sample


rm(list=ls())
# set the working directory
setwd("C:/Users/thoconne.ADS/Documents Backup - 102518/Avin/Kidney Disease Study/Human CKD/MMB Serum")

mmb.serum.dat <- read.csv("MMB_serum.csv")
mmb.serum.meta <- mmb.serum.dat[,1:4]
mmb.serum.mat <- as.matrix(mmb.serum.dat[,5:191]); rownames(mmb.serum.mat) <- mmb.serum.dat[,1]

# take row 1 as the reference sample and compute the total metabolite concentrations
ref.sample.sum <- sum(mmb.serum.dat[1,5:191])

# generate data frame for sum & normalization factors
norm <- data.frame(x = numeric(33), y = numeric(33))
norm[,1] <- apply(mmb.serum.mat, 1, sum) # column with sums for each sample
rownames(norm) <- mmb.serum.dat[,1]
colnames(norm) <- c("sums", "norm_factor")
norm[,2] <- ref.sample.sum/norm[,1]   # compute the norm factor for each sample


# apply the normalization to the original matrix dataset 

mmb.serum.mat.norm <- mmb.serum.mat*norm[,2]

