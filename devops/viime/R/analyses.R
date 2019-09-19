
#' wilcoxon_test_z_scores
#'
#' @export
wilcoxon_test_z_scores <- function(measurements, groups) {
  Metab = read.csv(measurements, row.names=1)
  groups = read.csv(groups, row.names=1)

  # take the first column
  Group = as.factor(groups[, 1])

  # create a table for p-values
  serum.wilcox <- data.frame(a=colnames(Metab), x=numeric(ncol(Metab)), y=numeric(ncol(Metab)), z=numeric(ncol(Metab)))
  colnames(serum.wilcox) <- c("Metabolite", "Wilcoxon", "Bonferroni", "Hochberg")

  # calculate Wilcoxon p-values
  for(i in 1:ncol(Metab)) {
    serum.wilcox.dat <- wilcox.test(Metab[, i] ~ Group)
    serum.wilcox[i,2] <- as.numeric(gsub("$p.value [1]", "", serum.wilcox.dat[3]))
  }
  # calculate adjusted p-value
  serum.wilcox[,3] <- p.adjust(serum.wilcox$Wilcoxon, method="bonferroni")
  serum.wilcox[,4] <- p.adjust(serum.wilcox$Wilcoxon, method="hochberg")

  serum.wilcox
}


#' anova_tukey_adjustment
#'
#' @export
anova_tukey_adjustment <- function(measurements, groups) {
  Metab = read.csv(measurements, row.names=1)
  groups = read.csv(groups, row.names=1)

  # take the first column
  Group = as.factor(groups[, 1])

  library(car) #For Type III ANOVA
  library(emmeans) #For pairwise comparisons https://cran.r-project.org/web/packages/emmeans/vignettes/comparisons.html

  # based on the given R code
  OUT <- NULL
  for (n in colnames(Metab)){
    mod <- lm(Metab[[n]] ~ Group)
    a <- Anova(mod, type="III")
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

  OUT
}
