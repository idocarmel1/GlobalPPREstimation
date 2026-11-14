# Reproduce the official Ecosense.GOA balance with unmodified pinned Rpath code.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==3)
source_dir <- normalizePath(args[1], winslash='/', mustWork=TRUE)
out_dir <- normalizePath(args[2], winslash='/', mustWork=TRUE)
library_dir <- normalizePath(args[3], winslash='/', mustWork=TRUE)
.libPaths(c(library_dir, .libPaths()))
options(digits=17, scipen=999, warn=1)
library(data.table)
setDTthreads(1)
source(file.path(source_dir,'Rpath_param.R'),encoding='UTF-8')
source(file.path(source_dir,'Rpath_ecopath.R'),encoding='UTF-8')

# Decimal exports carry 17 significant digits; RDS retains exact R objects.
csv_exact <- function(x,name) {
  x <- as.data.frame(x,check.names=FALSE,stringsAsFactors=FALSE)
  x[] <- lapply(x,function(v) {
    if (is.numeric(v)) return(ifelse(is.na(v),'',sprintf('%.17g',v)))
    if (is.logical(v)) return(ifelse(is.na(v),'',ifelse(v,'TRUE','FALSE')))
    ifelse(is.na(v),'',as.character(v))
  })
  write.table(x,file.path(out_dir,name),sep=',',row.names=FALSE,col.names=TRUE,
              quote=TRUE,na='',fileEncoding='UTF-8',eol='\n')
}
matrix_csv <- function(x,name,row_name) {
  frame <- data.frame(row=rownames(x),x,check.names=FALSE,stringsAsFactors=FALSE)
  names(frame)[1] <- row_name
  csv_exact(frame,name)
}
params <- read.rpath.params(file.path(source_dir,'Ecosense_GOA_base.csv'),
                            file.path(source_dir,'Ecosense_GOA_diet.csv'),
                            file.path(source_dir,'Ecosense_GOA_pedigree.csv'))
stopifnot(nrow(params$model)==50,sum(params$model$Type==0)==46,
          sum(params$model$Type==1)==1,sum(params$model$Type==2)==2,
          sum(params$model$Type==3)==1,params$stanzas$NStanzaGroups==0)
params_before <- serialize(params,NULL,version=3)
source_model <- copy(params$model)
source_diet <- copy(params$diet)
csv_exact(params$model,'reader_model.csv')
csv_exact(params$diet,'reader_diet.csv')

# The archived R object is independent source evidence, not silently substituted.
rda_env <- new.env(parent=emptyenv())
rda_names <- load(file.path(source_dir,'Ecosense.GOA.rda'),envir=rda_env)
archived <- rda_env[['Ecosense.GOA']]
rda_comparison <- lapply(c('model','diet','pedigree'),function(field) {
  cmp <- all.equal(as.data.frame(params[[field]]),as.data.frame(archived[[field]]),
                   tolerance=0,check.attributes=TRUE)
  data.frame(component=field,equal=isTRUE(cmp),detail=paste(cmp,collapse=';'))
})
csv_exact(do.call(rbind,rda_comparison),'rda_csv_comparison.csv')
writeLines(c(paste('RDA objects:',paste(rda_names,collapse=',')),
             capture.output(str(archived,max.level=2))),file.path(out_dir,'rda_structure.txt'))

captured_warnings <- character()
balanced <- withCallingHandlers(
  rpath(params,eco.name='Gulf of Alaska (Ecosense.GOA)',eco.area=291840),
  warning=function(w) {captured_warnings <<- c(captured_warnings,conditionMessage(w));invokeRestart('muffleWarning')})
stopifnot(identical(params_before,serialize(params,NULL,version=3)))
saveRDS(balanced,file.path(out_dir,'native_balanced.rds'),version=3,compress='xz')
stopifnot(identical(balanced,readRDS(file.path(out_dir,'native_balanced.rds'))))
writeLines(captured_warnings,file.path(out_dir,'native_warnings.txt'))
writeLines(capture.output(sessionInfo()),file.path(out_dir,'session_info.txt'))
writeLines(capture.output(str(balanced,max.level=1)),file.path(out_dir,'balanced_structure.txt'))

ids <- seq_len(balanced$NUM_GROUPS)
living <- which(balanced$type<2)
dead <- which(balanced$type==2)
gears <- which(balanced$type==3)
biological <- which(balanced$type<3)
detinput <- source_model$DetInput;detinput[is.na(detinput)] <- 0
groups <- data.frame(Group=balanced$Group,Type=balanced$type,Biomass=balanced$Biomass,
  PB=balanced$PB,QB=balanced$QB,EE=balanced$EE,GE=balanced$GE,TL=balanced$TL,
  BA=balanced$BA,Unassim=balanced$Unassim,DetInput=detinput,
  Landings=rowSums(balanced$Landings),Discards=rowSums(balanced$Discards),
  Catch=rowSums(balanced$Landings+balanced$Discards),check.names=FALSE,row.names=NULL)
csv_exact(groups[biological,],'groups.csv')
csv_exact(groups,'groups_with_fleet.csv')
matrix_csv(balanced$DC,'diet.csv','Prey')
matrix_csv(balanced$DetFate[biological,,drop=FALSE],'detritus_fate.csv','Group')
matrix_csv(balanced$DetFate,'detritus_fate_with_fleet.csv','Group')
matrix_csv(balanced$Landings,'landings.csv','Group')
matrix_csv(balanced$Discards,'discards.csv','Group')
csv_exact(data.frame(Group=balanced$Group[living],diet_sum=colSums(balanced$DC)),
          'diet_sums.csv')

# Independent direct formulation: all 47 living B values are source supplied;
# only EE is unknown. A is diagonal B*PB, b=C+BA+sum(predatorQ*diet).
stopifnot(all(!is.na(source_model$Biomass[living])),all(is.na(source_model$EE[living])))
living_production <- source_model$Biomass[living]*source_model$PB[living]
living_q <- source_model$Biomass[living]*balanced$QB[living]
prey_consumption <- as.numeric(balanced$DC[biological,,drop=FALSE] %*% living_q)
catch_all <- groups$Catch[biological]
b_rhs <- catch_all[living]+source_model$BioAcc[living]+prey_consumption[living]
A <- diag(living_production);dimnames(A)<-list(balanced$Group[living],balanced$Group[living])
singular <- svd(A,nu=0,nv=0)$d
svd_tolerance <- max(singular)*.Machine$double.eps
rank_svd <- sum(singular>svd_tolerance)
direct_EE <- b_rhs/living_production
living_residual <- living_production*balanced$EE[living]-b_rhs
csv_exact(data.frame(Group=balanced$Group[living],Production=living_production,
  Catch=catch_all[living],BA=source_model$BioAcc[living],Predation=prey_consumption[living],
  Native_EE=balanced$EE[living],Direct_EE=direct_EE,
  EE_difference=balanced$EE[living]-direct_EE,Residual=living_residual,
  Relative_residual=living_residual/pmax(abs(b_rhs),.Machine$double.eps)),
  'living_balance_audit.csv')
matrix_csv(A,'living_A.csv','Group')
csv_exact(data.frame(Group=balanced$Group[living],b=b_rhs),'living_b.csv')

# Separate natural detritus, discarded catch, external inputs and interpool transfer.
natural_loss <- groups$Biomass[living]*groups$PB[living]*(1-groups$EE[living])+
                groups$Biomass[living]*groups$QB[living]*groups$Unassim[living]
natural_inputs <- colSums(natural_loss*balanced$DetFate[living,,drop=FALSE])
fleet_discards <- colSums(balanced$Discards)
fleet_inputs <- colSums(fleet_discards*balanced$DetFate[gears,,drop=FALSE])
# Native code adds the DetInput vector to each fate column; all source values are 0.
external_inputs <- rep(sum(detinput),length(dead))
first_inputs <- natural_inputs+fleet_inputs+external_inputs
det_outputs <- prey_consumption[dead]
unused <- pmax(first_inputs-det_outputs,0)
interpool_inputs <- colSums(unused*balanced$DetFate[dead,,drop=FALSE])
total_inputs <- first_inputs+interpool_inputs
det_residual <- total_inputs*balanced$EE[dead]-det_outputs
csv_exact(data.frame(Group=balanced$Group[dead],Natural_input=natural_inputs,
  Fleet_discard_input=fleet_inputs,External_input=external_inputs,
  Interpool_input=interpool_inputs,Total_input=total_inputs,Consumption=det_outputs,
  Native_EE=balanced$EE[dead],Direct_EE=det_outputs/total_inputs,
  Native_Biomass=balanced$Biomass[dead],Source_PB=source_model$PB[dead],
  Direct_Biomass=total_inputs/source_model$PB[dead],Residual=det_residual,
  Unused_input=total_inputs-det_outputs),'detritus_balance_audit.csv')

# Parameter-change ledger includes native structural defaults and solved values.
ledger <- list();k<-0
fields <- c(Biomass='Biomass',PB='PB',QB='QB',EE='EE',ProdCons='GE',BioAcc='BA',Unassim='Unassim',DetInput='DetInput')
for (i in biological) for (field in names(fields)) {
  old <- source_model[[field]][i];new <- groups[[fields[[field]]]][i]
  action <- if (is.na(old)) {
    if (field=='EE') 'native balance equation' else if(field=='Biomass') 'detritus inflow divided by source PB' else if(field=='ProdCons') 'native PB/QB or structural zero' else 'native structural zero for unavailable/nonfeeding field'
  } else if (identical(as.numeric(old),as.numeric(new))) 'unchanged' else 'native derived value; inspect residual'
  k<-k+1;ledger[[k]]<-data.frame(Group=groups$Group[i],Field=field,Source=old,Runtime=new,
     Source_missing=is.na(old),Runtime_missing=is.na(new),Transformation=action)
}
for (i in biological) {
 k<-k+1;ledger[[k]]<-data.frame(Group=groups$Group[i],Field='TL',Source=NA_real_,Runtime=groups$TL[i],Source_missing=TRUE,Runtime_missing=FALSE,Transformation='native trophic-level linear solve')
}
csv_exact(do.call(rbind,ledger),'source_runtime_parameter_ledger.csv')
raw_diet <- as.matrix(source_diet[,-1,with=FALSE])
diet_ledger <- expand.grid(Prey=source_diet[[1]],Predator=balanced$Group[living],stringsAsFactors=FALSE)
diet_ledger$Source <- as.vector(raw_diet)
diet_ledger$Runtime <- as.vector(balanced$DC)
diet_ledger$Source_missing <- is.na(diet_ledger$Source)
diet_ledger$Transformation <- ifelse(diet_ledger$Source_missing,'native NA-to-zero convention','unchanged source fraction; no normalization')
csv_exact(diet_ledger,'source_runtime_diet_ledger.csv')

metrics <- c(living_groups=length(living),biological_groups=length(biological),fleets=length(gears),
  rank_svd=rank_svd,rank_qr=qr(A)$rank,dimension=nrow(A),svd_tolerance=svd_tolerance,
  condition_number=max(singular)/min(singular),smallest_singular_value=min(singular),
  largest_singular_value=max(singular),max_living_abs_residual=max(abs(living_residual)),
  max_living_relative_residual=max(abs(living_residual/pmax(abs(b_rhs),.Machine$double.eps))),
  max_living_EE_difference=max(abs(balanced$EE[living]-direct_EE)),
  max_detritus_abs_residual=max(abs(det_residual)),
  max_detritus_B_difference=max(abs(balanced$Biomass[dead]-total_inputs/source_model$PB[dead])),
  min_EE=min(balanced$EE[biological]),max_EE=max(balanced$EE[biological]),
  EE_outside_zero_one=sum(balanced$EE[biological]<0|balanced$EE[biological]>1),
  nonfinite_group_parameters=sum(!is.finite(as.matrix(groups[biological,c('Biomass','PB','QB','EE','GE','TL','BA','Unassim','DetInput')]))),
  minimum_living_biomass=min(balanced$Biomass[living]),
  total_model_landings=sum(groups$Landings[biological]),
  total_model_discards=sum(groups$Discards[biological]),
  source_diet_NA_to_zero=sum(is.na(raw_diet)),
  source_unchanged=as.numeric(identical(params_before,serialize(params,NULL,version=3))))
csv_exact(data.frame(metric=names(metrics),value=as.numeric(metrics)),'metrics.csv')
stopifnot(rank_svd==length(living),max(abs(living_residual))<1e-9,
          max(abs(balanced$EE[living]-direct_EE))<1e-12,
          max(abs(det_residual))<1e-9)
cat('NATIVE RPATH BALANCE COMPLETED\n')
print(metrics)
