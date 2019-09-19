#' imputation
#'
#' Return a new dataframe with NaN values imputed using magic.
#'   Missing Not At Random (MNAR)
#'   Missing Completely At Random (MCAR)
#'   Missing At Random (MAR)
#'
#'   p_mnar:
#'     Percent to define Missing Not At Random (MNAR), variables
#'     with any one group with more or equal than x% of missing data
#'   p_mcar:
#'     Percent to define Missing Not At Random (MCAR), variables with all
#'     group with less or equal than x% of missing data
#'   mnar:
#'     "zero" or "half-minimum"
#'   mcar:
#'     "random-forest", "knn", "mean", or "median"
#' @export
imputation <- function(table, groups,
                       mnar="zero", mcar="random-forest",
                       p_mnar=0.70, p_mcar=0.40) {
  table <- read.csv(table, row.names = 1)
  if (sum(colSums(is.na(table))) == 0) {
    return(table)
  }

  groups <- read.csv(groups, row.names = 1)

  #-#-#-#-# Function for missing percentage #-#-#-#-#

  # Create function to calculate percentage of missing data
  mean_na <- function(x){
    mean(is.na(x))
  }


  #-#-#-#-# Imputation algorithms #-#-#-#-#

  #-#-# Algorithms for Missing Not At Random (MNAR)

  #-# Imputation Zero #-#

  #Create function for imputation

  imputation_zero <- function(x){
    x[is.na(x)] <- 0
    return(x)
  }


  #-# Imputation HM (Half of the Minimum) #-#

  imputation_hm <- function(x){
    imputation <- lapply(x, function(y) {
      y[is.na(y)] <- min(y, na.rm = TRUE) / 2
      y
    })
    hm_imp <- as.data.frame(imputation)
    return(hm_imp)
  }



  #-#-# Algorithms for Missing Completely at Random (MCAR)
  #          and Missing At Random (MAR)

  #-# Imputation Random Forest #-#
  #Create function for imputation

  imputation_rf <- function(x){
    imputation <- missForest::missForest(x)
    rf_imp <- imputation$ximp
    return(rf_imp)
  }


  #-# Imputation kNN #-#

  imputation_knn <- function(x){
    imputation <- impute::impute.knn(t(x))
    knn_imp <- as.data.frame(t(imputation$data))
    return(knn_imp)
  }


  #-# Imputation Mean #-#

  imputation_mean <- function(x){
    imputation <- lapply(x, function(y) {
      y[is.na(y)] <- mean(y, na.rm = TRUE)
      y
    })
    mean_imp <- as.data.frame(imputation)
    return(mean_imp)
  }


  #-# Imputation Median #-#

  imputation_median <- function(x){
    imputation <- lapply(x, function(y) {
      y[is.na(y)] <- median(y, na.rm = TRUE)
      y
    })
    median_imp <- as.data.frame(imputation)
    return(median_imp)
  }

  if (mnar == "zero") {
    f_mnar <- imputation_zero
  } else if (mnar == "half-minimum") {
    f_mnar <- imputation_hm
  } else {
    stop("Invalid mnar parameter")
  }

  if (mcar == "random-forest") {
    f_mcar <- imputation_rf
  } else if (mcar == "knn") {
    f_mcar <- imputation_knn
  } else if (mcar == "mean") {
    f_mcar <- imputation_mean
  } else if (mcar == "median") {
    f_mcar <- imputation_median
  } else {
    stop("Invalid mcar parameter")
  }

  #-#-#-#-# Identify variables in MNAR, MCAR and MAR group #-#-#-#-#

  # Use function to calculate percentage of missing values per metabolite per
  # Group
  missing_pct <- aggregate(table, by = groups, mean_na)


  #-# MNAR variables #-#

  # Identify variables with at least one group with more than p.mnar of missing
  # data
  var_keep <- as.data.frame(
    colSums(missing_pct[, 2:ncol(missing_pct)] >= p_mnar)
  )
  colnames(var_keep) <- c("var")

  # Keep variables with at least one group with more than p.mnar of missing data
  var_keep_mnar <- subset(var_keep, var >= 1)

  # Set of variables with at least one group with more than p.mnar of missing
  # data
  new_metab_dat_mnar <- table[row.names(var_keep_mnar)]


  #-# MCAR variables #-#

  # Identify variables with all group with less or equal than mcar of missing
  # data
  var_keep <- as.data.frame(
    colSums(missing_pct[, 2:ncol(missing_pct)] <= p_mcar)
  )
  colnames(var_keep) <- c("var")

  # Keep variables with all group with less or equal than mcar of missing data
  var_keep_mcar <- subset(var_keep, var == nlevels(groups[, ]))

  # Set of variables with all group with less or equal than mcar of missing data
  new_metab_dat_mcar <- table[row.names(var_keep_mcar)]

  # imputation:
  imp_mnar <- f_mnar(new_metab_dat_mnar)
  imp_mcar <- f_mcar(new_metab_dat_mcar)

  # merge
  comp_imp <- cbind(imp_mnar, imp_mcar)

  # replace in the input table
  table[colnames(comp_imp)] < comp_imp[colnames(comp_imp)]

  # impute MAR
  return(f_mcar(table))
}
