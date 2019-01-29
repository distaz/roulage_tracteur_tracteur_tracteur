library(clue)

TTFL1 <- read.csv("C:/Users/DI STASIO/Desktop/TTFL/TTFL.csv",sep=",",header = F)
noms <- read.csv("C:/Users/DI STASIO/Desktop/TTFL/noms.csv",sep=",", header = F)
dates <- read.csv("C:/Users/DI STASIO/Desktop/TTFL/calendrier.csv",sep=",",header = F)
historique <- read.delim("C:/Users/DI STASIO/Desktop/TTFL/Histo Marco.txt",sep="\t", header = F, quote=)

historique <- historique[,c(1,2)]
rownames(TTFL1)<-noms$V1
colnames(TTFL1)<-as.Date(dates$V1)
TTFL1 <- TTFL1[,order(colnames(TTFL1))]

histo=c()

for (i in 1:length(historique$V1)){
  temp=strsplit(as.character(historique$V2[i]),", ")
  histo=c(histo,paste(temp[[1]][2],temp[[1]][1]))
}

h=0
for (j in 1:length(noms$V1)){
  joueur=rownames(TTFL1)[j]
  for (i in 1:30){
    if (TTFL1[j,i]<0 || is.na(TTFL1[j,i]) || is.null(TTFL1[j,i])){
      TTFL1[j,i]=0
    }
  }
  if (joueur %in% histo){
    h=h+1
    for (i in 1:30){
      if (TTFL1[j,i]<0 || is.na(TTFL1[j,i])){
        TTFL1[j,i]=0
      }
      if (as.Date(colnames(TTFL1)[i])-as.Date(historique$V1[which(histo==joueur)[1]])<30){
        TTFL1[j,i]=0
      }
    }
  }
}


#Joueurs blessés
blesses=c("LeBron James", "Anthony Davis", "Clint Capela")
for (i in 1:length(blesses)){
  TTFL1[which(rownames(TTFL1)==blesses[i]),]=0
}




result<-solve_LSAP(t(as.matrix(TTFL1)),maximum = T)

picks=noms[result,1]

## Check des meilleurs pour un soir choisi
jour=1
data <- TTFL1[order(TTFL1[jour],decreasing = T),]
data[jour]

## Scores du deck prédit

deck <- data.frame(0)
for (i in 1:length(picks)){
  deck[i,1] <- levels(picks)[c(picks[i])]
  deck[i,2] <- TTFL1[rownames(TTFL1)==levels(picks)[c(picks[i])],i]
}
colnames(deck) <- c("Joueurs","Score prédit")
deck

write.csv2(deck,"C:/Users/DI STASIO/Desktop/TTFL/Deck_05-01-19.csv")



