

# Set the working directory
setwd("C:/Users/lgolzarr/Box Sync/EBIO Consulting/O'Connell, Tom/Metabolomics/Transformations")

# Reading data
serum.dat <- read.csv("Concentrations_031119_complete.csv")

# Only metabolite data
m.data <- serum.dat[,3:46]


#-#-#-#---- Centering ----#-#-#-#

#-# Creating function using apply
center_apply <- function(x) {
  apply(x, 2, function(y) y - mean(y) )
}

# apply it
center.m.data <- as.data.frame(center_apply(m.data))




#-#-#-#---- Scaling ----#-#-#-#


#-#-- Autoscaling --#-#

#-# Creating function using apply
auto_apply <- function(x) {
  apply(x, 2, function(y) (y - mean (y))/ sd(y) )
}

# apply it
auto.m.data<- as.data.frame(auto_apply(m.data))


#-#-- Range scaling --#-#

#-# Creating function using apply
range_apply <- function(x) {
  apply(x, 2, function(y) (y - mean (y))/ (max(y)-min(y)) )
}

# apply it
range.m.data <- as.data.frame(range_apply(m.data))


#-#-- Pareto scaling --#-#

#-# Creating function using apply
pareto_apply <- function(x) {
  apply(x, 2, function(y) (y - mean (y))/ sqrt(sd(y)) )
}

# apply it
pareto.m.data<- as.data.frame(pareto_apply(m.data))


#-#-- Vast scaling --#-#

#-# Creating function using apply
vast_apply <- function(x) {
  apply(x, 2, function(y) (y - mean (y))/ sd(y) * mean(y)/sd(y) )
}

# apply it
vast.m.data<- as.data.frame(vast_apply(m.data))


#-#-- Level scaling --#-#

#-# Creating function using apply
level_apply <- function(x) {
  apply(x, 2, function(y) (y - mean (y))/ mean(y) )
}

# apply it
level.m.data<- as.data.frame(level_apply(m.data))




#-#-#-#---- Transformations ----#-#-#-#


#-#-- Log Transformation --#-#

#-# Creating function using apply for log transform, I added (0.00000001) to allow log function on zero
log_apply <- function(x) {
  apply(x, 2, function(y) log10(y+0.00000001) )
}

# apply it
log.m.data<- as.data.frame(log_apply(m.data))

#then centered with center function already created
center.log.m.data <- as.data.frame(center_apply(log.m.data))


#-#-- Power Transformation --#-#

#-# Creating function using apply for log transform,I added (0.00000001) to allow log function on zero
power_apply <- function(x) {
  apply(x, 2, function(y) sqrt(y) )
}

# apply it
power.m.data<- as.data.frame(power_apply(m.data))

#then centered with center function already created
center.power.m.data <- as.data.frame(center_apply(power.m.data))




########################
#-#-# PCA Plots for each of them

#Load packages
#install.packages("ggfortify")
library(ggfortify) #let {ggplot2} know how to interpret PCA objects

#Plot principal components by Treatment
#Original data
p <- autoplot(prcomp(m.data), data = serum.dat, colour = 'Group') +
              ggtitle('PCA for Original Data') 
p

#Centering
p1 <- autoplot(prcomp(center.m.data), data = serum.dat, colour = 'Group') +
               ggtitle('PCA for Centering Data') 
p1

#Autoscaling
p2 <- autoplot(prcomp(auto.m.data), data = serum.dat, colour = 'Group') +
               ggtitle('PCA for Autoscaling Data') 
p2

#Range scaling
p3 <- autoplot(prcomp(range.m.data), data = serum.dat, colour = 'Group') +
               ggtitle('PCA for Range Scaling Data') 
p3 

#Pareto Scaling
p4 <- autoplot(prcomp(pareto.m.data), data = serum.dat, colour = 'Group') +
               ggtitle('PCA for Pareto Scaling Data') 
p4

#Vast Scaling
p5 <- autoplot(prcomp(vast.m.data), data = serum.dat, colour = 'Group') +
               ggtitle('PCA for Vast Scaling Data') 
p5

#Level Scaling
p6 <- autoplot(prcomp(level.m.data), data = serum.dat, colour = 'Group') +
               ggtitle('PCA for Level Scaling Data') 
p6 

#Log transfomation
p7 <- autoplot(prcomp(log.m.data), data = serum.dat, colour = 'Group') +
               ggtitle('PCA for Log transform Data') 
p7 

#Log transform and centering
p8 <- autoplot(prcomp(center.log.m.data), data = serum.dat, colour = 'Group') +
               ggtitle('PCA for Log transform and centering Data') 
p8 

#Power transformation
p9 <- autoplot(prcomp(power.m.data), data = serum.dat, colour = 'Group') +
               ggtitle('PCA for Power transform Data') 
p9

#Power transform and centering
p10 <- autoplot(prcomp(center.power.m.data), data = serum.dat, colour = 'Group') +
                ggtitle('PCA for Power transform and centering Data') 
p10



########################
#-#-# Loadings Plots for each of them

# load library
library(ggplot2)

# Create backgroud graph for all
theta <- seq(0,2*pi,length.out = 100)
circle <- data.frame(x = cos(theta), y = sin(theta))
q <- ggplot(circle,aes(x,y)) + geom_path()



#Original data
loadings <- data.frame(prcomp(m.data)$rotation, 
                       .names = row.names(prcomp(m.data)$rotation))
q + geom_text(data=loadings, 
              mapping=aes(x = PC1, y = PC2, label = .names, colour = .names), show.legend=FALSE) +
  coord_fixed(ratio=1) +
  labs(x = "PC1", y = "PC2", title="Loadings plot for Original Data")

#Centering
loadings <- data.frame(prcomp(center.m.data)$rotation, 
                       .names = row.names(prcomp(center.m.data)$rotation))
q + geom_text(data=loadings, 
              mapping=aes(x = PC1, y = PC2, label = .names, colour = .names), show.legend=FALSE) +
  coord_fixed(ratio=1) +
  labs(x = "PC1", y = "PC2", title="Loadings plot for Centering Data")

#Autoscaling
loadings <- data.frame(prcomp(auto.m.data)$rotation, 
                       .names = row.names(prcomp(auto.m.data)$rotation))
q + geom_text(data=loadings, 
              mapping=aes(x = PC1, y = PC2, label = .names, colour = .names), show.legend=FALSE) +
  coord_fixed(ratio=1) +
  labs(x = "PC1", y = "PC2", title="Loadings plot for Autoscaling Data")

#Range scaling
loadings <- data.frame(prcomp(range.m.data)$rotation, 
                       .names = row.names(prcomp(range.m.data)$rotation))
q + geom_text(data=loadings, 
              mapping=aes(x = PC1, y = PC2, label = .names, colour = .names), show.legend=FALSE) +
  coord_fixed(ratio=1) +
  labs(x = "PC1", y = "PC2", title="Loadings plot for Range Scaling Data")

#Pareto Scaling
loadings <- data.frame(prcomp(pareto.m.data)$rotation, 
                       .names = row.names(prcomp(pareto.m.data)$rotation))
q + geom_text(data=loadings, 
              mapping=aes(x = PC1, y = PC2, label = .names, colour = .names), show.legend=FALSE) +
  coord_fixed(ratio=1) +
  labs(x = "PC1", y = "PC2", title="Loadings plot for Pareto Scaling Data")

#Vast Scaling
loadings <- data.frame(prcomp(vast.m.data)$rotation, 
                       .names = row.names(prcomp(vast.m.data)$rotation))
q + geom_text(data=loadings, 
              mapping=aes(x = PC1, y = PC2, label = .names, colour = .names), show.legend=FALSE) +
  coord_fixed(ratio=1) +
  labs(x = "PC1", y = "PC2", title="Loadings plot for Vast Scaling Data")

#Level Scaling
loadings <- data.frame(prcomp(level.m.data)$rotation, 
                       .names = row.names(prcomp(level.m.data)$rotation))
q + geom_text(data=loadings, 
              mapping=aes(x = PC1, y = PC2, label = .names, colour = .names), show.legend=FALSE) +
  coord_fixed(ratio=1) +
  labs(x = "PC1", y = "PC2", title="Loadings plot for Level Scaling Data")

#Log transfomation
loadings <- data.frame(prcomp(log.m.data)$rotation, 
                       .names = row.names(prcomp(log.m.data)$rotation))
q + geom_text(data=loadings, 
              mapping=aes(x = PC1, y = PC2, label = .names, colour = .names), show.legend=FALSE) +
  coord_fixed(ratio=1) +
  labs(x = "PC1", y = "PC2", title="Loadings plot for Log transform Data")

#Log transform and centering
loadings <- data.frame(prcomp(center.log.m.data)$rotation, 
                       .names = row.names(prcomp(center.log.m.data)$rotation))
q + geom_text(data=loadings, 
              mapping=aes(x = PC1, y = PC2, label = .names, colour = .names), show.legend=FALSE) +
  coord_fixed(ratio=1) +
  labs(x = "PC1", y = "PC2", title="Loadings plot for Log transform and centering Data")

#Power transformation
loadings <- data.frame(prcomp(power.m.data)$rotation, 
                       .names = row.names(prcomp(power.m.data)$rotation))
q + geom_text(data=loadings, 
              mapping=aes(x = PC1, y = PC2, label = .names, colour = .names), show.legend=FALSE) +
  coord_fixed(ratio=1) +
  labs(x = "PC1", y = "PC2", title="Loadings plot for Power transform Data")

#Power transform and centering
loadings <- data.frame(prcomp(center.power.m.data)$rotation, 
                       .names = row.names(prcomp(center.power.m.data)$rotation))
q + geom_text(data=loadings, 
              mapping=aes(x = PC1, y = PC2, label = .names, colour = .names), show.legend=FALSE) +
  coord_fixed(ratio=1) +
  labs(x = "PC1", y = "PC2", title="Loadings plot for Power transform and centering Data")

