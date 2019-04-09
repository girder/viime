rm(list=ls())

#-#-#-# Imputation of missing data for metabolites #-#-#-#

# Install library For knn imputation
if (!requireNamespace("BiocManager", quietly = TRUE))
  install.packages("BiocManager")
BiocManager::install("impute", version = "3.8")

#Load library 
library(impute)

# set the working directory
#setwd("D:/Documents Backup - 102518/Kubal/Kubal NMR Data 030819/Kubal NMR Data/Chenomx files 030819")
setwd("C:/Users/lgolzarr/Box Sync/EBIO Consulting/O'Connell, Tom/Metabolomics/Missing data")

# Reading data
serum.dat <- read.csv("Concentrations_031119_trial.csv")



#-#-#-# STEP 1 : filter out if all groups have more than 25% of missing data #-#-#-#

# Calculate percetage of missing data overall
# colMeans(is.na(serum.dat))

# Create function to calculate percentage of missing data
mean.na <- function(x){
  mean(is.na(x))
}

# Use function to calculate percentage of missing values per metabolite per Group
missing.pct <- aggregate(serum.dat[,6:ncol(serum.dat)], by = list(serum.dat$Group), mean.na)

# For first filter (filter variables based on exhibiting presence in at least
#  75% of samples in at least one of n groups.)
# Identify variables that all groups have higher than 25% of missing data

var.keep <- as.data.frame(colSums(missing.pct[,2:ncol(missing.pct)]>0.25))
colnames(var.keep) <- c("na.higher.25")

#Delete variables that have more than 25% of missing data in all of their groups
var.keep.1 <- subset(var.keep, !na.higher.25==nlevels(serum.dat$Group))

#Metabolites staying
row.names(var.keep.1)

#New data set with first filter
clean.serum.dat <- serum.dat[c("Group",row.names(var.keep.1))]



#-#-#-# STEP 2 : variables with any one group with more or equal than 70% of missing data, impute zero #-#-#-#

# Use function to calculate percentage of missing values per metabolite per Group
missing.pct <- aggregate(clean.serum.dat[,2:ncol(clean.serum.dat)], by = list(clean.serum.dat$Group), mean.na)

# Identify variables with at least one group with more than 70% of missing data
var.keep <- as.data.frame(colSums(missing.pct[,2:ncol(missing.pct)]>=0.70))
colnames(var.keep) <- c("na.higher.70")

# Keep variables with at least one group with more than 70% of missing data
var.keep.2 <- subset(var.keep, na.higher.70>=1)

#Metabolites for imputation 0
row.names(var.keep.2)

#Set of variables with at least one group with more than 70% of missing data
clean.serum.dat.s2 <- clean.serum.dat[row.names(var.keep.2)]

#Replace NA to zero for those variables
clean.serum.dat.s2[is.na(clean.serum.dat.s2) ] <- 0



#-#-#-# STEP 3 : variables with all group with less or equal than 40% of missing data, impute KNN#-#-#-#

# Set of variables without STEP 2 variables
clean.serum.dat.s3 <- clean.serum.dat[, -which(names(clean.serum.dat) %in% row.names(var.keep.2))]

# Use function to calculate percentage of missing values per metabolite per Group
missing.pct <- aggregate(clean.serum.dat.s3[,2:ncol(clean.serum.dat.s3)], by = list(clean.serum.dat.s3$Group), mean.na)

# Identify variables with all group with less or equal than 40% of missing data
var.keep <- as.data.frame(colSums(missing.pct[,2:ncol(missing.pct)]<=0.40))
colnames(var.keep) <- c("na.less.40")

##### Problem, I am keeping also variables in STEP 1, I need to correct that
# Keep variables with all group with less or equal than 40% of missing data
var.keep.3 <- subset(var.keep, na.less.40==nlevels(clean.serum.dat.s3$Group))

# Metabolites for imputation kNN 
row.names(var.keep.3)

# Data set with only metabolites for imputation kNN, no Group variable
clean.serum.dat.s3 <- clean.serum.dat.s3[row.names(var.keep.3)]


# Imputation kNN
Rseed <- 12345 #Random seed for replication
clean.serum.dat.s3 <- as.data.frame(t(impute.knn(t(clean.serum.dat.s3), rng.seed=Rseed)$data))



#-#-#-# STEP 4 : variables with 40% to 70 % missing data, impute KNN (rest of variables)#-#-#-#

# Set of variable imputed until now
clean.serum.dat.s4 <- cbind(clean.serum.dat.s2, clean.serum.dat.s3)

# Create dataset with all variables (imputed in step 1 and 2, and the one that still have missing values)
clean.serum.imp <- clean.serum.dat
clean.serum.imp[colnames(clean.serum.dat.s4)] <- clean.serum.dat.s4[colnames(clean.serum.dat.s4)]

# Imputation kNN
Rseed <- 12345 #Random seed for replication
clean.serum.imp <- as.data.frame(t(impute.knn(t(clean.serum.imp[,2:ncol(clean.serum.imp)]), rng.seed=Rseed)$data))

# COMPLETE data set with all metabolites imputed
clean.serum.imp <- cbind(Group = clean.serum.dat$Group, clean.serum.imp)


#To corroborate that there is no missing data, this should be zero
mean(is.na(clean.serum.imp))




# ----- Generate Z-scores from data -----
#Load packages
library(ggfortify) #let {ggplot2} know how to interpret PCA objects

data1 <- clean.serum.imp[,2:ncol(clean.serum.imp)]

autoplot(prcomp(data1, scale = FALSE), data = clean.serum.imp, colour = 'Group')
