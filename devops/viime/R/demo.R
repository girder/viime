#' Example R processing function.
#'
#' This is adapted from Muscle_all_metab_anova_tukey_foldchange.R.

demo <- function(table) {
  # set the working directory
  muscle.dat <- read.csv(table)

  # --------------- calculate ANOVA p-value ---------------------------------------------------------

  muscle.aov <- data.frame(x=character(43), y=numeric(43))
  muscle.aov[,1] <- colnames(muscle.dat[,3:45])
  colnames(muscle.aov) <- c("muscle Metab", "AoV p-val")
  groups <- muscle.dat$Musc.Metab

  for(i in 3:45) {
      muscle.aov.dat <- aov(muscle.dat[,i] ~ groups)
      muscle.aov[i-2,2] <- summary(muscle.aov.dat)[[1]][[1,"Pr(>F)"]]
  }

  # --------------- generate table of Tukey multiple comparison test p-values -----------------------

  tukey.table <- data.frame(Fol__ACVR2B.fc=numeric(43), Fol.ACVR2B.fc__ACVR2B.fc=numeric(43),
                            Veh__ACVR2B.fc = numeric(43), Fol.ACVR2B.fc__Fol = numeric(43),
                            Veh__Fol = numeric(43), Veh__Fol.ACVR2B.fc = numeric(43))
  rownames(tukey.table) <- colnames(muscle.dat[,3:45])

  for(i in 3:43) {
    muscle.tukey.dat <- as.data.frame((TukeyHSD(aov(muscle.dat[,i] ~ groups)))[1])
    tukey.table[i-2,1:6] <- muscle.tukey.dat$groups.p.adj
  }

  # ----- generate table of fold changes -----------------------------------------------------------

  #muscle.FC.table <- data.frame(Veh_ACRR2B.Fc=numeric(121), Veh_Fol=numeric(121), Veh_Fol.ACRR2B.Fc = numeric(121))

  muscle.FC.table <- data.frame(FC_Veh_ACVR2B=numeric(43), Log2FC_Veh_ACVR2B=numeric(43),
                               FC_Veh_Fol    =numeric(43), Log2FC_Veh_Fol   =numeric(43),
                               FC_Fol.ACVR2B =numeric(43), Log2FC_Fol.ACVR2B=numeric(43))

  rownames(muscle.FC.table) <- colnames(muscle.dat[,3:45])


  #for(i in 3:123) {
  #  muscle.mean.dat <- aggregate(muscle.dat[,i] ~ Group, muscle.dat, mean)
  #                    muscle.FC.table[i-2,1] <- (abs(muscle.mean.dat[1,2] - muscle.mean.dat[4,2]))/muscle.mean.dat[4,2]
  #                    muscle.FC.table[i-2,2] <- (abs(muscle.mean.dat[2,2] - muscle.mean.dat[4,2]))/muscle.mean.dat[4,2]
  #                    muscle.FC.table[i-2,3] <- (abs(muscle.mean.dat[3,2] - muscle.mean.dat[4,2]))/muscle.mean.dat[4,2]
  #}
    
  for(i in 3:45) {
            muscle.mean.dat <- aggregate(muscle.dat[,i] ~ groups, muscle.dat, mean)
            muscle.FC.table[i-2,1] <- (abs(muscle.mean.dat[1,2] - muscle.mean.dat[4,2]))/muscle.mean.dat[4,2]
            muscle.FC.table[i-2,2] <- log(muscle.FC.table[i-2,1],2)
            
            muscle.FC.table[i-2,3] <- (abs(muscle.mean.dat[2,2] - muscle.mean.dat[4,2]))/muscle.mean.dat[4,2]
            muscle.FC.table[i-2,4] <- log(muscle.FC.table[i-2,3],2)
            
            muscle.FC.table[i-2,5] <- (abs(muscle.mean.dat[3,2] - muscle.mean.dat[4,2]))/muscle.mean.dat[4,2]
            muscle.FC.table[i-2,6] <- log(muscle.FC.table[i-2,5],2)
  }

  return (muscle.FC.table)
}
