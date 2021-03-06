#install.packages("stringr", dependencies=TRUE)
#install.packages("clue", dependencies=TRUE)

library(clue)
library(stringr)

config <- readLines("config.ini")

for (i in 1 : length(config)){
  if (str_sub(config[i], 2, str_length(config[i])-1) == "csv"){
    PATH_TO_WRITE = str_split_fixed(config[i+1], " : ", 2)[1,2]
  }
  if (str_sub(config[i], 2, str_length(config[i])-1) == "joueur"){
    PLAYERS = str_split(str_split(config[i+1], " : ")[[1]][2], ", ")[[1]]
  }
  if (str_sub(config[i], 2, str_length(config[i])-1) == "blesse"){
    BLESS = str_split(str_split(config[i+1], " : ")[[1]][2], ", ")[[1]]
  }
}

for (iter in 1 : length(PLAYERS)){

  TTFL1 <- read.csv(str_c(PATH_TO_WRITE, "/TTFL.csv"),sep=";",header = TRUE)
  historique <- read.delim(str_c(PATH_TO_WRITE, "/Histo_", PLAYERS[iter], ".txt"),sep="\t", header = F, quote=)[,c(1,2)]
  
  rownames(TTFL1)<-TTFL1$Nom
  TTFL1 <- TTFL1[-1]
  TTFL1 <- TTFL1[,order(colnames(TTFL1))]
  list_col = colnames(TTFL1)
  for (i in 1:length(list_col)){
	list_col[i] = substring(list_col[i], 2)
	list_col[i] = gsub("\\.", "-", list_col[i])
  }
  colnames(TTFL1) = list_col
  
  histo=c()
  for (i in 1:length(historique$V1)){
    temp=strsplit(as.character(historique$V2[i]),", ")
    histo=c(histo,paste(temp[[1]][2],temp[[1]][1]))
  }
  
  h=0
  for (j in 1:nrow(TTFL1)){
    joueur=rownames(TTFL1)[j]
    for (i in 1:length(TTFL1)){
      if (TTFL1[j,i]<0 || is.na(TTFL1[j,i]) || is.null(TTFL1[j,i])){
        TTFL1[j,i]=0
      }
    }
    if (joueur %in% histo){
      h=h+1
      for (i in 1:length(TTFL1)){
        if (TTFL1[j,i]<0 || is.na(TTFL1[j,i])){
          TTFL1[j,i]=0
        }
        if (as.Date(colnames(TTFL1)[i])-as.Date(historique$V1[which(histo==joueur)[1]])<30){
          TTFL1[j,i]=0
        }
      }
    }
  }
  
  
  #Joueurs bless�s
  #blesses=c("LeBron James", "Anthony Davis", "Clint Capela")
  for (i in 1:length(BLESS)){
    TTFL1[which(rownames(TTFL1)==BLESS[i]),]=0
  }
  
  
  
  
  result<-solve_LSAP(t(as.matrix(TTFL1)),maximum = T)
  
  picks=rownames(TTFL1)[result]
  
  ## Check des meilleurs pour un soir choisi
  jour=1
  data <- TTFL1[order(TTFL1[jour],decreasing = T),]
  #data[jour]
  
  ## Scores du deck pr�dit
  
  deck <- data.frame(0)
  for (i in 1:length(picks)){
    deck[i,1] <- picks[i]
    deck[i,2] <- TTFL1[rownames(TTFL1)==picks[i], i]
  }
  colnames(deck) <- c("Joueurs","Score pr�dit")
  
  
  
  write.table(deck, file = str_c(PATH_TO_WRITE, "/", PLAYERS[iter], "_DECK_", Sys.Date(), ".txt"))
  write.table(data[jour], file = str_c(PATH_TO_WRITE, "/", PLAYERS[iter], "_PREDICT_", Sys.Date(), ".txt"))
}
