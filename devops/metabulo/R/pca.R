#' Basic PCA plot
#'
#' Uses MetaboAnalystR's PlotPCAPairSummary method

pca_overview_plot <- function(table) {
  library(MetaboAnalystR)
  # most of this seems to be required to get the PCA and plotting methods to work
  mSet<-InitDataObjects("conc", "stat", FALSE);
  mSet<-Read.TextData(mSet, table, "rowu", "disc");
  mSet<-SanityCheckData(mSet);
  mSet<-RemoveMissingPercent(mSet, percent=0.5);
  mSet<-ImputeVar(mSet, method="min");
  mSet<-PreparePrenormData(mSet);
  mSet<-Normalization(mSet, "NULL", "NULL", "NULL", ratio=FALSE, ratioNum=20);
  mSet<-PCA.Anal(mSet);

  pclabels <- paste("PC", 1:5, "\n", round(100*mSet$analSet$pca$variance[1:5],1), "%");
  if(mSet$dataSet$cls.type == "disc"){
    pairs(mSet$analSet$pca$x[,1:5], PCH=as.numeric(mSet$dataSet$cls)+1, labels=pclabels);
  }else{
    pairs(mSet$analSet$pca$x[,1:5], labels=pclabels);
  }
}
