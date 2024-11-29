#!/bin/bash
#SBATCH -J pcr
#SBATCH --mail-type=end
#SBATCH --mail-user=michel.kunkler@tum.de
#SBATCH -o ./%x.%j.%N.out
#SBATCH -D ./
#SBATCH --get-user-env
#SBATCH --cluster=serial
#SBATCH --partition=serial_std
#SBATCH --mem=1000mb
#SBATCH --cpus-per-task=1
#SBATCH --export=NONE
#SBATCH --time=78:00:00
DURATION_HOURS=78

ulimit -s 8192
ulimit -n 1024

export TMPDIR="/dss/dsshome1/00/ge35xof4/tmp" 
export TMP="/dss/dsshome1/00/ge35xof4/tmp"
export TEMP="/dss/dsshome1/00/ge35xof4/tmp"

module load slurm_setup
module load r/4.1.2-gcc11-mkl gdal proj geos sqlite glib
module rm intel-mpi intel
module load gcc/11

module load user_spack
#spack install dmtcp
spack load dmtcp

#spack load freetype@2.7.1%intel@21.4.0 arch=linux-sles15-haswell 
#spack load /fdkrhz7 #harfbuzz 
#spack load fribidi@1.0.5%gcc@11.2.0 arch=linux-sles15-haswell 
#module restore my_r_env 

#R -e "tempdir()" 
#R -e "install.packages('curl', repos = 'http://cran.us.r-project.org')" 
#R -e "install.packages('purrr', repos = 'http://cran.us.r-project.org')" 
#R -e "install.packages('sf', repos = 'http://cran.us.r-project.org')" 
#R -e "install.packages('cleandata', repos = 'http://cran.us.r-project.org')" 
#R -e "install.packages('devtools', repos = 'http://cran.us.r-project.org')" 
#module save my_r_env 

date
echo $1
cd $1
dmtcp_coordinator --coord-logfile coord_log.log --daemon --port 0 --port-file ./coordinator
sleep 1
time ./train.sh $DURATION_HOURS
sleep 3600
