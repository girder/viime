library("MetaboAnalystR");

mSet<-InitDataObjects("conc", "stat", FALSE);
mSet<-Read.TextData(mSet, "https://www.metaboanalyst.ca/MetaboAnalyst/resources/data/human_cachexia.csv", "rowu", "disc");
mSet<-SanityCheckData(mSet);
mSet<-RemoveMissingPercent(mSet, percent=0.5);
mSet<-ImputeVar(mSet, method="min")
mSet<-PreparePrenormData(mSet);
mSet<-Normalization(mSet, "MedianNorm", "NULL", "MeanCenter", ratio=FALSE, ratioNum=20);
mSet<-PlotNormSummary(mSet, "norm_0_", "png", 72, width=NA);
mSet<-PlotSampleNormSummary(mSet, "snorm_0_", "png", 72, width=NA);
