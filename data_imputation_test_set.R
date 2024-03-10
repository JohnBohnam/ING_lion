#R session setup####
setwd("C:/Users/danie/OneDrive/Pulpit/ING challange/")
rm(list=ls())
gc()
library(dplyr)
library(magrittr)
library(ggplot2)
#data inspection####
data <- read.csv(file = "test_data.csv")
data %>%  attach() 

#renaming####
data %<>% rename(no_applicants=Var1,
                 loan_purpose=Var2,
                 y=target,
                 distr_channel=Var3,
                 application_ammout=Var4,
                 credit_duration=Var5,
                 payment_frequency=Var6,
                 installment_ammount=Var7,
                 car_value=Var8,
                 income_M=Var9,
                 income_S=Var10,
                 profession_M=Var11,
                 profession_S=Var12,
                 empl_date_M=Var13,
                 material_status_M=Var14,
                 no_children_M=Var15,
                 no_dependencies_M=Var16,
                 spendings=Var17,
                 property_ownership_renovation=Var18,
                 car_or_motorbike=Var19,
                 requests_3m=Var20,
                 requests_6m=Var21,
                 requests_9m=Var22,
                 requests_12m=Var23,
                 credit_card_limit=Var24,
                 account=Var25,
                 savings=Var26,
                 arrear_3m=Var27,
                 arrear_12m=Var28,
                 credit_score=Var29,
                 income=Var30)

#merge with Maciek####
data %<>% filter(Application_status=="Approved") 
maciek <- read.csv(file = "testing_dla_daniela.csv")
data <- merge(data,maciek,by="ID")
data %<>% select(-c(X,ID,customer_id,X_r_))
data[data$Var35==Inf,"Var35"] <- 0
data %<>% select(-Application_status) 
#data type
data %<>% mutate_at(c('y','loan_purpose','distr_channel','profession_M','profession_S','material_status_M','property_ownership_renovation','car_or_motorbike','arrear_3m','arrear_12m','credit_score'),as.factor)
data_debug <- data
rm(maciek)
#NA check
summary(data)
levels(data$loan_purpose) <- c("car","house","cash")
all(!(data$loan_purpose=="car")==(is.na(data$car_or_motorbike)),na.rm = T)
all(!(data$loan_purpose=="car")==(is.na(data$car_value)),na.rm = T)
all(!(data$loan_purpose=="house")==(is.na(data$property_ownership_renovation)),na.rm = T)
all((is.na(data$income_S))==(is.na(data$profession_S)))
#missing at random check
aggregate((as.numeric(data$y)-1)~is.na(data$loan_purpose), FUN=mean)
aggregate((as.numeric(data$y)-1)~is.na(data$income_S), FUN=mean)
aggregate((as.numeric(data$y)-1)~is.na(data$spendings), FUN=mean)
aggregate((as.numeric(data$y)-1)~is.na(data$account), FUN=mean)
aggregate((as.numeric(data$y)-1)~is.na(data$savings), FUN=mean)
#credit score monotonicity
cs=aggregate((as.numeric(data$y)-1)~data$credit_score, FUN=mean)
#plot(as.numeric(as.character(cs[,1])),cs[,2],xlab = "credit score",ylab="average pd in the bucket")
data_cs_bucketed <- data %>% mutate(credit_score=cut(as.numeric(as.character(credit_score)),c(-1,0,10,20,30,70,100,250)))
aggregate((as.numeric(data_cs_bucketed$y)-1)~data_cs_bucketed$credit_score, FUN=mean)
data <- data %>% mutate(credit_score=cut(as.numeric(as.character(credit_score)),c(-1,0,10,20,30,70,100,250)))
rm(cs)
rm(data_cs_bucketed)
# work_b4_aplication

Sys.setlocale("LC_TIME", "English")
date_convert <- function(D){as.Date(unlist(lapply(strsplit(D," "),function(L){L[1]})),"%d%B%Y")}
data %<>% mutate(application_date=date_convert(application_date),
                 empl_date_M=date_convert(empl_date_M))
data %<>% mutate(empl_to_app_time=as.numeric(application_date-empl_date_M))
mean(as.numeric((data %>% filter(empl_to_app_time<0) %>% select(y))$y)-1)
#high pd for unemployed => flag required
data %<>% mutate(is_unemployed=(empl_to_app_time<0)) 
data %<>% mutate(empl_to_app_time=pmax(empl_to_app_time,0))
data %<>% select(-c(application_date,empl_date_M))
rm(date_convert)
#flag installation####
data %<>% mutate(secondary_applicant=(!is.na(profession_S)),
                 savings_na=is.na(savings),
                 account_na=is.na(account),
                 spendings_na=is.na(spendings))
#NA to 0 or factor level
data %<>% mutate(profession_S=as.factor(ifelse(is.na(profession_S), "N_A", profession_S)),
                 loan_purpose=as.factor(ifelse(is.na(loan_purpose), "N_A", loan_purpose)),
                 property_ownership_renovation=as.factor(ifelse(is.na(property_ownership_renovation), "N_A", property_ownership_renovation)),
                 car_or_motorbike=as.factor(ifelse(is.na(car_or_motorbike), "N_A", car_or_motorbike))) 
data[,c("account","car_value","income_S","spendings","savings")][is.na(data[, c("account","car_value","income_S","spendings","savings")])] <- 0
x=as.character(data$distr_channel)
x[x=="1"] <- "Direct"
x[x=="2"] <- "Broker"
x[x=="3"] <- "Online"
x[x==""] <- "NA"
x %<>% as.factor() 
data$distr_channel <- x
rm(x)

types=sapply(data, class)
factors=colnames(data)[types=="factor"]
par(mfrow=c(4,3))
pdf("factors.pdf")
sapply(factors,function(x){tt=aggregate((as.numeric(data$y)-1)~(data[,x]), FUN=mean);
plot(tt[,1],tt[,2],main=x,ylim(0,0.2))})
dev.off()
tt=aggregate((as.numeric(data$y)-1)~data$loan_purpose, FUN=mean)
flags=colnames(data)[types=="logical"]
pdf("flags.pdf")
sapply(flags,function(x){tt=aggregate((as.numeric(data$y)-1)~as.factor((data[,x])), FUN=mean);
plot(tt[,1],tt[,2],main=x,ylim(0,0.2))})
dev.off()
numer=colnames(data)[types%in%c("integer","numeric")]
x=numer[1]
pdf("numeric.pdf")
numeric_plot <- function(x){
  data_zero=data[data$y=="0",]
  data_one=data[data$y=="1",]
  p1 <- hist(data_zero[,x],freq= F,col=rgb(0,0,1,1/4),main=x,xlab=x,ylab="density of y",ylim=c(0,max((hist(data_zero[,x],plot = F))$density,(hist(data_one[,x],plot = F))$density)))                     # centered at 4
  p2 <- hist(data_one[,x],freq = F,col=rgb(1,0,0,1/4),add=T) 
  legend("topright",legend=c("y==0","y==1"),fill=c(rgb(0,0,1,1/4),rgb(1,0,0,1/4)))  # centered at 6
}
sapply(numer, numeric_plot)
dev.off()
write.csv(data,"imputed_data.csv")
data_2 <- read.csv("imputed_data.csv")
