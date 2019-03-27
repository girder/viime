
#' imputation
#'
#' Return a new dataframe with NaN values imputed using magic.
imputation <- function (table, groups) {
    library(impute)
    mean.na <- function(x){
      mean(is.na(x))
    }

    table = read.csv(table, row.names=1)
    groups = read.csv(groups, row.names=1)

    #-#-#-# STEP 1 : variables with any one group with more or equal than 70% of missing data, impute zero #-#-#-#

    # Use function to calculate percentage of missing values per metabolite per Group
    missing.pct <- aggregate(table, by=groups, mean.na)

    # Identify variables with at least one group with more than 70% of missing data
    var.keep <- as.data.frame(colSums(missing.pct[,2:ncol(missing.pct)]>=0.70))
    colnames(var.keep) <- c("na.higher.70")

    # Keep variables with at least one group with more than 70% of missing data
    var.keep.2 <- subset(var.keep, na.higher.70>=1)

    #Metabolites for imputation 0
    row.names(var.keep.2)

    #Set of variables with at least one group with more than 70% of missing data
    clean.dat.s2 <- table[row.names(var.keep.2)]

    #Replace NA to zero for those variables
    clean.dat.s2[is.na(clean.dat.s2) ] <- 0


    #-#-#-# STEP 2 : variables with all group with less or equal than 40% of missing data, impute KNN#-#-#-#

    # Set of variables without STEP 1 variables
    clean.dat.s3 <- table[, -which(names(table) %in% row.names(var.keep.2))]

    # Use function to calculate percentage of missing values per metabolite per Group
    missing.pct <- aggregate(clean.dat.s3, by=groups, mean.na)

    # Identify variables with all group with less or equal than 40% of missing data
    var.keep <- as.data.frame(colSums(missing.pct[,2:ncol(missing.pct)]<=0.40))
    colnames(var.keep) <- c("na.less.40")

    # JB: I don't think this is an issue since python does the filtering (masking).
    ##### Problem, I am keeping also variables in STEP 0, I need to correct that
    # Keep variables with all group with less or equal than 40% of missing data
    var.keep.3 <- subset(var.keep, na.less.40>=nlevels(groups[,]))

    # Data set with only metabolites for imputation kNN, no Group variable
    clean.dat.s3 <- clean.dat.s3[row.names(var.keep.3)]


    # Imputation kNN
    # Rseed <- 12345 #Random seed for replication
    clean.dat.s3 <- as.data.frame(t(impute.knn(t(clean.dat.s3))$data))

    #-#-#-# STEP 3 : variables with 40% to 70 % missing data, impute KNN (rest of variables)#-#-#-#

    # Set of variable imputed until now
    clean.dat.s4 <- cbind(clean.dat.s2, clean.dat.s3)

    # Create dataset with all variables (imputed in step 1 and 2, and the one that still have missing values)
    clean.imp <- table
    clean.imp[colnames(clean.dat.s4)] <- clean.dat.s4[colnames(clean.dat.s4)]

    # Imputation kNN
    return(as.data.frame(t(impute.knn(t(clean.imp))$data)))
}
