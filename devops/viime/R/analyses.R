
#' wilcoxon_test_z_scores
#'
#' @export
wilcoxon_test_z_scores <- function(measurements, groups, log_transformed=FALSE) {
  Metab = read.csv(measurements, row.names=1, check.names=FALSE)
  groups = read.csv(groups, row.names=1, check.names=FALSE)

  # take the first column
  Group = as.factor(groups[, 1])


  compute <- function(prefix, groupA, groupB) {
    # create a table for p-values
    result <- data.frame(x=numeric(ncol(Metab)), y=numeric(ncol(Metab)), z=numeric(ncol(Metab)), u=numeric(ncol(Metab)))
    colnames(result) <- paste0(prefix, c("Wilcoxon", "Bonferroni", "Hochberg", "Log2FoldChange"))

    # calculate Wilcoxon p-values
    for(i in 1:ncol(Metab)) {
      a <- Metab[Group == groupA, i]
      b <- Metab[Group == groupB, i]
      dat <- tryCatch(
        wilcox.test(as.numeric(a), as.numeric(b)),
        error=function(err) {
            return(err)
        }
      )

      # check if 'dat' is an error by checking if it inherits
      # from the 'error' class
      if (inherits(dat, "error")) {
        return(data.frame(error=dat$message))
      }

      result[i,1] <- as.numeric(gsub("$p.value [1]", "", dat[3]))

      # calculate fold change
      if (log_transformed) {
        result[i,4] <- mean(b) - mean(a)
      } else {
        result[i,4] <- log2(mean(b) / mean(a))
      }
    }
    # calculate adjusted p-value
    result[,2] <- p.adjust(result[,1], method="bonferroni")
    result[,3] <- p.adjust(result[,1], method="hochberg")


    result
  }

  combinations = combn(levels(Group), 2)
  OUT = data.frame(Metabolite=colnames(Metab))

  if (ncol(combinations) == 1) {
    groupA <- combinations[1, 1]
    groupB <- combinations[2, 1]

    sub = compute("", groupA, groupB)
    OUT = cbind(OUT, sub)
  } else {
    for(j in 1:ncol(combinations)) {
      groupA <- combinations[1, j]
      groupB <- combinations[2, j]

      sub = compute(paste0(groupA, " - ", groupB, " "), groupA, groupB)
      OUT = cbind(OUT, sub)
    }
  }

  OUT
}


#' anova_tukey_adjustment
#'
#' @export
anova_tukey_adjustment <- function(measurements, groups, log_transformed=FALSE) {
  Metab = read.csv(measurements, row.names=1, check.names=FALSE)
  groups = read.csv(groups, row.names=1, check.names=FALSE)

  # take the first column
  Group = as.factor(groups[, 1])

  library(car) #For Type III ANOVA
  library(emmeans) #For pairwise comparisons https://cran.r-project.org/web/packages/emmeans/vignettes/comparisons.html

  # based on the given R code
  OUT <- NULL
  for (n in colnames(Metab)){
    mod <- lm(Metab[[n]] ~ Group)

    # catches any possible errors thrown by ANOVA and returns them
    a <- tryCatch(
        Anova(mod, type="III"),
        error=function(err) {
            return(err)
        }
      )

    # check if 'a' is an error by checking if it inherits
    # from the 'error' class
    if (inherits(a, "error")) {
      return(data.frame(error=a$message))
    }

    x1 <- cbind(n,t(a[,"Pr(>F)"] ))

    emm.mod <- emmeans(mod, "Group")
    b <- pairs(emm.mod)
    x2 <- summary(b)$p.value
    x2 <- t(x2)
    colnames(x2) <- summary(b)$contrast

    x <- cbind(x1,x2)
    OUT <- rbind(OUT, x)
    colnames(OUT) <- c("Metabolite", row.names(a), colnames(x2))
    rm(mod,a,b,x1,x2,x)
  }

  # compute fold changes
  combinations = combn(levels(Group), 2)
  for(j in 1:ncol(combinations)) {
    groupA <- combinations[1, j]
    groupB <- combinations[2, j]

    sub <- data.frame(x=numeric(ncol(Metab)))
    colnames(sub) <- c(paste0(groupA, " - ", groupB, " Log2FoldChange"))

    for(i in 1:ncol(Metab)) {
      a <- Metab[Group == groupA, i]
      b <- Metab[Group == groupB, i]
      # calculate fold change
      if (log_transformed) {
        sub[i,1] <- mean(b) - mean(a)
      } else {
        sub[i,1] <- log2(mean(b) / mean(a))
      }
    }
    OUT = cbind(OUT, sub)
  }

  OUT
}


#' clustered_heatmap
#'
#' @export
clustered_heatmap <- function(measurements) {
  Metab = read.csv(measurements, row.names=1)

  scaled = scale(as.matrix(Metab), center = TRUE, scale = TRUE)

  OUT = as.data.frame(scaled)
  colnames(OUT) = colnames(Metab)
  rownames(OUT) = rownames(Metab)

  x = as.matrix(OUT)

  Rowv = rowMeans(x)
  distr = dist(x)
  hcr = hclust(distr)
  ddr = as.dendrogram(hcr)
  ddr = reorder(ddr, Rowv)
  # rowInd = order.dendrogram(ddr)

  Colv = colMeans(x)
  distc = dist(t(x))
  hcc = hclust(distc)
  ddc = as.dendrogram(hcc)
  ddc = reorder(ddc, Colv)
  # colInd = order.dendrogram(ddc)

  f <- textConnection('OUT_CSV', 'w')
  write.csv(OUT, f)
  close(f)

  list(data=OUT_CSV, row=unclass(ddr), col=unclass(ddc))
}

#' roc_analysis
#'
#' @export
roc_analysis <- function(measurements, groups, group1_name, group2_name, column_names, method) {
  library(pROC)
  library(randomForest)
  df <- read.csv(measurements, row.names=1, check.names=TRUE)
  groups <- read.csv(groups, row.names=1, check.names=TRUE)
  groups <- as.factor(groups[, 1])

  group_mask <- numeric() # intialize empty numeric vector
  for (i in groups) {
    if (i == group1_name) {
        group_mask <- c(group_mask, 0)
    } else if (i == group2_name) {
        group_mask <- c(group_mask, 1)
    }
  }

  # make sure row order is preserved
  if (group_mask[1] == 0) {
    # remove all rows not in group1 or group2
    df <- rbind(df[groups == group1_name,], df[groups == group2_name,])
  } else {
    df <- rbind(df[groups == group2_name,], df[groups == group1_name,])
  }


  column_names <- read.csv(column_names, row.names=1, check.names=TRUE)
  c <- unlist(column_names) # convert dataframe to a vector
  c <- make.names(c) # convert column names to valid R names
  columns <- df[c] # only select the columns/metabolites we want
  new <- cbind(group_mask, columns)

  if (method == "logistic_regression") {
    #-# Logistic Regression
    glm.fit <- glm(group_mask ~ . , family=binomial, data=new)
    pred <- glm.fit$fitted.values
  } else if (method == "random_forest") {
    #-# Random forest
    rf.model <- randomForest::randomForest(factor(group_mask)~ ., data=new)
    pred <- rf.model$votes[,1]
  } else {
    stop("Invalid method")
  }

  #############
  #ROC analysis
  roc.a <- pROC::roc(group_mask, pred, plot=FALSE)

  # Confidence interval
  d <- pROC::ci.sp(roc.a)
  rocci.df <- as.data.frame(cbind(y=as.numeric(rownames(d)),d[,c(1,3)]))
  rocci.df$`lower_bound` <- 1-rocci.df$`2.5%`
  rocci.df$`upper_bound` <- 1-rocci.df$`97.5%`
  rocci.df <- as.data.frame(rocci.df[,c(1,4,5)]*100)
  
  return(list(data.frame(
      sensitivities=roc.a$sensitivities,
      specificities=roc.a$specificities,
      thresholds=roc.a$thresholds,
      auc=rep(roc.a$auc, length(roc.a$thresholds))
    ),
    rocci.df
  ))
}

#' factor_analysis
#'
#' @export
factor_analysis <- function(measurements, threshold) {
  library(psych)

  m.df <- read.csv(measurements, row.names=1, check.names=FALSE)

  ##########################################
  # Code for factor analysis


  #-#-#- Defining number of factors we need -#-#-#
  #- (Eigenvalues higher than 1) -#

  # Principal Component Analysis to get eigenvalues
  m.df <- m.df[ , which(apply(m.df, 2, var) != 0)]
  pca_a <- prcomp(m.df, center=T, scale=T)

  #getting the eigenvalues
  MS.eig <- (pca_a$sdev)^2

  #Eigenvalues higher than 1 to see how many factors we need
  ncomp <- sum(MS.eig >= 1)

  ##############################
  #-#-#- Factor Analysis -#-#-#

  # Factor analysis
  #Using ncomp, number of components with eigenvalue higher than 1
  fitpsy <- psych::fa(m.df, nfactors=ncomp, rotate="varimax")

  #Save some results from factor analysis
  eigen.values <- fitpsy$e.values #eigenvalues
  loadings <- fitpsy$Structure[,1:ncomp] #Loadings
  Prop.var <- fitpsy$Vaccounted[2,] # Proportion of variance

  #################################
  #-#-#-# Table with Factors #-#-#-#

  #Create table of factors and what is metabolites are in each factor
  OUT=NULL
  for (i in 1:ncomp){
    a <- which(abs(loadings[,i]) >= threshold) #This is the line that chooses the metabolites with loading higher than lt
    if (length(a) == 0) { # if factor analysis returns zero metabolites, return empty dataframe
      OUT <- data.frame(metabolites <- character(),
                        eigenvalues <- numeric(),
                        variances <- numeric(),
                        factor <- numeric())
      return(OUT)
    }
    metabolites <- names(a)
    eigenvalues <- eigen.values[i]
    variances <- Prop.var[i]
    b <- cbind(factor=i, metabolites, eigenvalues, variances)
    OUT <- rbind(OUT,b)
  }
  out <- OUT
}

#' plsda
#'
#' @export
plsda <- function(measurements, groups, num_of_components) {
  library(mixOmics)
  df <- read.csv(measurements, row.names=1, check.names=FALSE)
  groups <- read.csv(groups, row.names=1, check.names=FALSE)
  groups <- as.factor(groups[,1])

  # PLS-DA (Set to scale=TRUE just for trial, for VIIME it should be FALSE since data has already been pretreated)
  mod_plsda <- mixOmics::plsda(df, groups, scale=FALSE, ncomp = num_of_components)

  # Save Scores
  scores_plsda <- data.frame(variates=mod_plsda$variates[1], explained_variance=as.list(mod_plsda$explained_variance$X))

  # Save loadings
  load_plsda <- as.data.frame(mod_plsda$loadings$X)

  # VIP scores/vip
  vip <- vip(mod_plsda)

  # R2/Q2 values
  Group_num <- as.numeric(as.factor(groups))
  mod_pls <- mixOmics::pls(df, Group_num, scale=FALSE, ncomp = num_of_components)
  qr <- mixOmics::perf(mod_pls, validation='loo')

  return(list(
    scores_plsda,
    load_plsda,
    vip,
    qr$R2,
    qr$Q2
  ))
}

#' oplsda
#'
#' @export
oplsda <- function(measurements, groups, num_of_components) {
  library(ropls)
  df <- read.csv(measurements, row.names=1, check.names=FALSE)
  groups <- read.csv(groups, row.names=1, check.names=FALSE)
  groups <- as.factor(groups[,1])

  # Perform OPLS-DA
  ropls_oplsda <- ropls::opls(df, groups, scaleC="none", orthoI=num_of_components)

  #Main Score
  ropls_scores_x  <- as.data.frame(ropls_oplsda@scoreMN)
  #Orthogonal
  ropls_scores_y  <- as.data.frame(ropls_oplsda@orthoScoreMN)
  #Save scores together
  oplsda_scores <- cbind(ropls_scores_x , ropls_scores_y)

  # Save loadings
  #Main loadings
  ropls_loadings_x  <- as.data.frame(ropls_oplsda@loadingMN)
  #Orthogonal loadings
  ropls_loadings_y  <- as.data.frame(ropls_oplsda@orthoLoadingMN)
  #Save loadings together
  oplsda_loadings <- cbind(ropls_loadings_x , ropls_loadings_y)

  #VIP Scores
  ropls_vip <- as.data.frame(ropls_oplsda@vipVn)

  return(list(
    oplsda_scores,
    oplsda_loadings,
    ropls_vip,
    ropls_oplsda@modelDF,
    ropls_oplsda@summaryDF
  ))
}
