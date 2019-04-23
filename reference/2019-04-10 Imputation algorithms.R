

#-#-#-#-# First defining data #-#-#-#-#

# set the working directory
setwd("C:/Users/lgolzarr/Box Sync/EBIO Consulting/O'Connell, Tom/Metabolomics/Missing data")
# Reading data
serum.dat <- read.csv("Concentrations_031119_trial.csv")

#Only metabolite data
metab.dat <- serum.dat[,6:ncol(serum.dat)]
#Only group data
group.dat <- serum.dat[,3]



#-#-#-#-# Defining parameters #-#-#-#-#

# Percent for filter variable out if all groups have more than x% of missing values
#Default
p.out <- 0.25

# Percent to define Missing Not At Random (MNAR), variables with any one group with more or equal than x% of missing data
#Default
p.mnar <- 0.70

# Percent to define Missing Not At Random (MCAR), variables with all group with less or equal than x% of missing data
#Default
p.mcar <- 0.40

# MAR would be variables between p.mcar and p.mnar missing data.



#-#-#-#-# Function for missing percentage #-#-#-#-# 

# Create function to calculate percentage of missing data
mean.na <- function(x){
  mean(is.na(x))
}


#-#-#-#-# Imputation algorithms #-#-#-#-#

#-#-# Algorithms for Missing Not At Random (MNAR)

#-# Imputation Zero #-#

#Create function for imputation

imputation.zero <- function(x){
  x[is.na(x)] <- 0
  return(x)
}


#-# Imputation HM (Half of the Minimum) #-#

imputation.hm <- function(x){
  imputation <- lapply(x, function(y) { 
    y[is.na(y)] <- min(y, na.rm = TRUE)/2
    y
  })
  hm.imp <- as.data.frame(imputation)
  return(hm.imp)
}



#-#-# Algorithms for Missing Completely at Random (MCAR) and Missing At Random (MAR)

#-# Imputation Random Forest #-#

# Install packages
install.packages("missForest")

#Load library 
library(missForest)

#Create function for imputation

imputation.rf <- function(x){
  imputation <- missForest(x)
  rf.imp <- imputation$ximp
  return(rf.imp)
}


#-# Imputation kNN #-#

# Install library For knn imputation
if (!requireNamespace("BiocManager", quietly = TRUE))
  install.packages("BiocManager")
BiocManager::install("impute", version = "3.8")

#Load library 
library(impute)

#Create seed and function for imputation
Rseed <- 12345
imputation.knn <- function(x){
  imputation <-impute.knn(t(x), rng.seed=Rseed) 
  knn.imp <- as.data.frame(t(imputation$data))
  return (knn.imp)
}


#-# Imputation Mean #-#

imputation.mean <- function(x){
  imputation <- lapply(x, function(y) { 
    y[is.na(y)] <- mean(y, na.rm = TRUE)
    y
  })
  mean.imp <- as.data.frame(imputation)
  return(mean.imp)
}


#-# Imputation Median #-#

imputation.median <- function(x){
  imputation <- lapply(x, function(y) { 
    y[is.na(y)] <- median(y, na.rm = TRUE)
    y
  })
  median.imp <- as.data.frame(imputation)
  return(median.imp)
}




#-#-#-#-# Identify variables to filter out #-#-#-#-#

### NOTE for Kitware
# If this step is going to be made in the screen with the data, then the data for imputation would 
# start as the dataset created in this part 'new.metab.dat', since the next steps should not  
# including those variables.

# Use function to calculate percentage of missing values per metabolite per Group
missing.pct <- aggregate(metab.dat, by = list(group.dat), mean.na)

# Identify variables that all groups have higher than p.out of missing data
var.ide <- as.data.frame(colSums(missing.pct[,2:ncol(missing.pct)]>p.out))
colnames(var.ide) <- c("var")

# Variables that have more than p.out of missing data in all of their groups
var.out <- subset(var.ide, var==nlevels(group.dat))

# Dataset without variables to drop out
new.metab.dat <- metab.dat[, -which(names(metab.dat) %in% row.names(var.out))]



#-#-#-#-# Identify variables in MNAR, MCAR and MAR group #-#-#-#-#

# Use function to calculate percentage of missing values per metabolite per Group
missing.pct <- aggregate(new.metab.dat, by = list(group.dat), mean.na)


#-# MNAR variables #-#

# Identify variables with at least one group with more than p.mnar of missing data
var.keep <- as.data.frame(colSums(missing.pct[,2:ncol(missing.pct)]>=p.mnar))
colnames(var.keep) <- c("var")

# Keep variables with at least one group with more than p.mnar of missing data
var.keep.mnar <- subset(var.keep, var>=1)

# Variables in MNAR 
row.names(var.keep.mnar)

# Set of variables with at least one group with more than p.mnar of missing data
new.metab.dat.mnar <- new.metab.dat[row.names(var.keep.mnar)]


#-# MCAR variables #-#

# Identify variables with all group with less or equal than mcar of missing data
var.keep <- as.data.frame(colSums(missing.pct[,2:ncol(missing.pct)]<=p.mcar))
colnames(var.keep) <- c("var")

# Keep variables with all group with less or equal than mcar of missing data
var.keep.mcar <- subset(var.keep, var==nlevels(group.dat))

# Variables in MCAR 
row.names(var.keep.mcar)

# Set of variables with all group with less or equal than mcar of missing data
new.metab.dat.mcar <- new.metab.dat[row.names(var.keep.mcar)]


#-# MAR variables #-#

#new.metab.dat.mar <- new.metab.dat[, -which(names(new.metab.dat) %in% row.names(rbind(var.keep.mnar,var.keep.mcar)))]




#-#-#-#-# Implement algorithms #-#-#-#-#

#Options of imputation
#For MNAR (f.mnar): imputation.zero, imputation.hm
#For MCAR/MAR (f.mcar): imputation.rf, imputation.knn, imputation.mean, imputation.median 
#Default MNAR: Zero, MCAR/MAR: RF

imputation <- function(complete, mnar, mcar, f.mnar = imputation.zero , f.mcar = imputation.rf){
  imp.mnar <- f.mnar(mnar) #imputing MNAR
  imp.mcar <- f.mcar(mcar) #Imputing MCAR
  comp.imp <- cbind(imp.mnar, imp.mcar) #Merging MNAR and MCAR imputation
  complete[colnames(comp.imp)] <- comp.imp[colnames(comp.imp)] #Replace already imputed variables
  imp.mar <- f.mcar(complete) #Impute MAR i.e. imputing rest of variables
  return(imp.mar)
}


#Examples

# Using defaults #MNAR: Zero, MCAR/MAR: rf 
Impa <- imputation(new.metab.dat, new.metab.dat.mnar, new.metab.dat.mcar)

#MNAR: Zero, MCAR/MAR: knn
Impb <- imputation(new.metab.dat, new.metab.dat.mnar, new.metab.dat.mcar,imputation.zero,imputation.knn)

#MNAR: Zero, MCAR/MAR: rf
Impc <- imputation(new.metab.dat, new.metab.dat.mnar, new.metab.dat.mcar,imputation.zero,imputation.rf)

#MNAR: Zero, MCAR/MAR: mean
Impd <- imputation(new.metab.dat, new.metab.dat.mnar, new.metab.dat.mcar,imputation.zero,imputation.mean)


