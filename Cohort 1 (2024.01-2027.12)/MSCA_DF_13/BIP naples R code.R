


###install the packages if you do not have them already
install.packages(c("imager","here","dplyr","broom","tidyverse", "ggplot"))

library(imager)
library(here)
library(dplyr)
library(broom)
library(ggplot2)
library(tidyverse)

######################################################################
### PART I: this is the code for ELVIS photo
###
###################################################################
img <- load.image(here("elvis-nixon.jpeg"))
plot(img)


str(img)
##  'cimg' num [1:800, 1:633, 1, 1] 0.914 0.929 0.91 0.906 0.898 ...
dim(img)
## [1] 800 633   1   1
img_df_long <- as.data.frame(img)
head(img_df_long)
img_df <- matrix(img_df_long$value, 800,633)  ##for elvis
dim(img_df)
img_df[1:5, 1:5]
img_pca<- prcomp(img_df,scale = TRUE, center = TRUE)
plot(img)
#############################################################
### this is the function to recover the picture from a given number of 
### components
############################################################

reverse_pca <- function(n_comp = 20, pca_object = img_pca){
  ## The pca_object is an object created by base R's prcomp() function.
  ## Multiply the matrix of rotated data by the transpose of the matrix 
  ## of eigenvalues (i.e. the component loadings) to get back to a 
  ## matrix of original data values
  recon <- pca_object$x[, 1:n_comp] %*% t(pca_object$rotation[, 1:n_comp])
 recon <- scale(recon, center = FALSE, scale = 1/pca_object$scale)
 recon <- scale(recon, scale = FALSE, center = -1 * pca_object$center)
 dims<- dim(img_pca$x)
x<-1:dims[1]
y<-1:dims[2]
 temp<- as.vector(as.matrix(recon))
tt<- expand.grid(x,y)
recon_df_long <- data.frame(pcs=n_comp, x=tt[,1], y=tt[,2], value=temp)
recon_df_long
}


########################################################

test1 <-reverse_pca(n_comp = 2, pca_object = img_pca)
test2<-reverse_pca(n_comp = 40, pca_object = img_pca)
test3<-reverse_pca(n_comp = 80, pca_object = img_pca)
test4<-reverse_pca(n_comp =120, pca_object = img_pca)
recovered_imgs<-rbind(test,test2,test3,test4)




p <- ggplot(data = recovered_imgs, 
            mapping = aes(x = x, y = y, fill = value))
p_out <- p + geom_raster() + 
  scale_y_reverse() + 
  scale_fill_gradient(low = "black", high = "white") +
  facet_wrap(~ pcs, ncol = 2) + 
  guides(fill = FALSE) + 
  labs(title = "Recovering the content of a pixel image\nfrom a Principal Components Analysis of its pixels") + 
  theme(strip.text = element_text(face = "bold", size = rel(1.2)),
        plot.title = element_text(size = rel(1.5)))
p_out










library(imager)
library(here)
library(dplyr)
library(broom)
library(ggplot2)
library(tidyverse)

img <- load.image(here("parrot.jpg"))
plot(img)
dim(img)

imgDm <- dim(img)
imgRGB <- data.frame(
  y = rep(imgDm[2]:1, each = imgDm[1]),
  x = rep(1:imgDm[1], imgDm[2]),
  R = as.vector(img[,,1]),
  G = as.vector(img[,,2]),
  B = as.vector(img[,,3])
  )


ggplot(data = imgRGB, aes(x = x, y = y)) + 
  geom_point(colour = rgb(imgRGB[c("R", "G", "B")])) +
  labs(title = paste("k-Means Clustering of", kClusters, "Colours")) +
  xlab("x") +
  ylab("y") 




################################################

kClusters <- 5
kMeans <- kmeans(imgRGB[, c("R", "G", "B")], centers = kClusters)
kColours <- rgb(kMeans$centers[kMeans$cluster,])
tau<- kMeans$centers[kMeans$cluster,]

ggplot(data = imgRGB, aes(x = x, y = y)) + 
  geom_point(colour = kColours) +
  labs(title = paste("k-Means Clustering of", kClusters, "Colours")) +
  xlab("x") +
  ylab("y")  

library(mclust)

model<- Mclust(imgRGB[, c("R", "G", "B")], G = 5)
kColours2 <- rgb(kMeans$centers[kMeans$cluster,])
kCol<- rgb(t(model$parameters$mean[,model$classification]))
ggplot(data = imgRGB, aes(x = x, y = y)) + 
  geom_point(colour = kCol) +
  labs(title = paste("k-Means Clustering of", kClusters, "Colours")) +
  xlab("x") +
  ylab("y") 




################################################################