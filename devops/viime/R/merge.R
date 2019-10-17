
#' compute_clean_pca
#'
#' @export
compute_clean_pca <- function(prefix, MS_metab) {
  # MS_metab = read.csv(measurements, row.names=1)
  
  ###
  #PCA for MS
  ###
  #Perform pca
  MS.pca <- prcomp(MS_metab, center = TRUE) #,scale. = TRUE #Center takes the mean of the column to all the values in the column
  
  #Saving the scores
  MS.pca.scores <- MS.pca$x
  #head(MS.pca.scores)
  
  #getting the standard deviations of the principal components (the square roots of the eigenvalues)
  MS.pca.sd <- MS.pca$sdev
  
  #getting the eigenvalues
  MS.eig <- (MS.pca$sdev)^2
  
  #transform the eigenvalues in Variances in percentage (0-1)
  MS.variance <- MS.eig/sum(MS.eig)
  
  #standardize scores=Scores divided by stdv
  MS.std.scores <- MS.pca.scores %*% diag(1 / MS.pca.sd)
  
  #Multiply standardize scores by percentages
  MS.scores.variance <- as.matrix(MS.std.scores) %*% diag(MS.variance)
  #head(MS.scores.variance)  ###This should be the matrix to concatenate
  
  #Change matrix to dataset
  MS.scores.variance <- as.data.frame(MS.scores.variance)
  MS.PC.names <- c(paste0(prefix, ".PC", 1:ncol(MS.scores.variance)))
  colnames(MS.scores.variance) <- MS.PC.names
  
  #Add patient ID
  rownames(MS.scores.variance) <- rownames(MS_metab)
  
  MS.scores.variance
}