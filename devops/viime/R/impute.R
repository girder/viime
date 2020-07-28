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
                       p_mnar=0.70, p_mcar=0.40, add_info=FALSE) {
  table <- read.csv(table, row.names = 1, check.names=FALSE)

  if (sum(colSums(is.na(table))) == 0) {
    if (add_info) {
      colnames(table) = paste0('A-', colnames(table))
    }
    # no missing values
    return(table)
  }

  groups <- read.csv(groups, row.names = 1, check.names=FALSE)

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
    rownames(hm_imp) <- rownames(x)
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
    rownames(mean_imp) <- rownames(x)
    return(mean_imp)
  }


  #-# Imputation Median #-#

  imputation_median <- function(x){
    imputation <- lapply(x, function(y) {
      y[is.na(y)] <- median(y, na.rm = TRUE)
      y
    })
    median_imp <- as.data.frame(imputation)
    rownames(median_imp) <- rownames(x)
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
  if (prod(dim(new_metab_dat_mnar)) > 0) {
    imp_mnar <- f_mnar(new_metab_dat_mnar)
  } else {
    imp_mnar <- new_metab_dat_mnar
  }
  if (prod(dim(new_metab_dat_mcar)) > 0) {
    imp_mcar <- f_mcar(new_metab_dat_mcar)
  } else {
    imp_mcar <- new_metab_dat_mcar
  }

  # merge
  comp_imp <- cbind(imp_mnar, imp_mcar)

  # replace in the input table
  out = table
  out[colnames(comp_imp)] <- comp_imp[colnames(comp_imp)]

  # impute mnar on colnames(new_metab_dat_mcar)
  # impute mcar on colnames(new_metab_dat_mcar)
  # imput mcar on all afterwards

  # impute MAR
  out <- f_mcar(out)

  if (add_info) {
    # encode the type of imputation in the column: A- ... as is, N- ... MNAR, C- ... MCAR
    base = colnames(out)
    with_meta_info = paste0('A-', base)
    done_mnar = row.names(var_keep_mnar)
    with_meta_info[base %in% done_mnar] = paste0('N-', base[base %in% done_mnar])

    # find column names which have some NA inside
    any_missing = names(which(sapply(table, anyNA)))
    # all other missing columns are either mcar or mar
    done_mcar_mar = setdiff(any_missing, done_mnar)

    with_meta_info[base %in% done_mcar_mar] = paste0('C-', base[base %in% done_mcar_mar])

    colnames(out) <- with_meta_info
  }

  return(out)
}
