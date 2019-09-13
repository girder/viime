#' Basic PCA plot
#'
#' Uses MetaboAnalystR's PlotPCAPairSummary method

anova_turkey_adjustment <- function(measurements, groups) {
  Metab = read.csv(measurements, row.names=1)
  groups = read.csv(groups)

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
