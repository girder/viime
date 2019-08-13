# This script carries out a simple "sum of all values" normalization method.  
# In this script, the sum of all of metabolite values for each sample is computed 
# and then a normalization facfor for each sample is computed by dividing 1000 by the sum.  
# Each metabolite value for a sample is then multiplied by this factor.
# As a result the sum of the metabolite values for each of the samples should = 1000

rm(list=ls())
# set the working directory
setwd("C:/Users/thoconne.ADS/Documents Backup - 102518/Avin/Kidney Disease Study/Human CKD/MMB Serum")

mmb.serum.dat <- read.csv("MMB_serum.csv")
mmb.serum.meta <- mmb.serum.dat[,1:4]
mmb.serum.mat <- as.matrix(mmb.serum.dat[,5:191]); rownames(mmb.serum.mat) <- mmb.serum.dat[,1]

# generate data frame for sum & normalization factors
norm <- data.frame(x = numeric(33), y = numeric(33), z= numeric(33))
rownames(norm) <- mmb.serum.dat[,1]
colnames(norm) <- c("Metab Sum", "Normfac", "NormTest")

# generate a colum with the total sum of metabolite values for each sample
norm[,1] <- apply(mmb.serum.mat, 1, sum)

# generate the normalization factor so that the sum of all metabolites for each sample is 1000
norm[,2] <- 1000/(norm[,1])

# apply the normalization to the original matrix dataset 

mmb.serum.mat.norm <- mmb.serum.mat*norm[,2]

# test to see if it worked

norm[,3] <- apply(mmb.serum.mat.norm, 1, sum) # make sure the final column is all 1000

# add the metadata back to the matrix to generate the normalized dataframe
mmb.serum.dat.norm <- cbind(mmb.serum.meta, mmb.serum.mat.norm)
