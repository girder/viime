#' column_masks
#'
#' Return a list of columns to mask given a group list and missing threshold.  This
#' function implements STEP 1 from the original imputation/filtering script.
column_masks <- function (table, groups, threshold) {
    # Create function to calculate percentage of missing data
    mean.na <- function(x){
      mean(is.na(x))
    }

    table = read.csv(table, row.names=1)
    groups = read.csv(groups, row.names=1)

    # Use function to calculate percentage of missing values per metabolite per Group
    missing.pct <- aggregate(table, by=groups, mean.na)

    # For first filter (filter variables based on exhibiting presence in at least
    #  1 - threshold of samples in at least one of n groups.)
    # Identify variables that all groups have higher than `threshold` fraction of missing data

    mask <- as.data.frame(colSums(missing.pct[,2:ncol(missing.pct)] > threshold))
    colnames(mask) <- c("mask")
    return(mask >= nlevels(groups[,]))
}
