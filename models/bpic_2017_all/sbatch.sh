#!/bin/bash
#SBATCH -J bpic_2017
#SBATCH --mail-type=end
#SBATCH --mail-user=michel.kunkler@tum.de
#SBATCH -o ./%x.%j.%N.out
#SBATCH -D ./
#SBATCH --get-user-env
#SBATCH --clusters=serial
#SBATCH --partition=serial_long
#SBATCH --mem=16000mb
#SBATCH --cpus-per-task=1
#SBATCH --export=NONE
#SBATCH --time=480:00:00

module load slurm_setup
module load r/4.1.2-gcc11-mkl gdal proj geos sqlite glib
module rm intel-mpi intel
module load gcc/11

module load user_spack
#spack load freetype@2.7.1%intel@21.4.0 arch=linux-sles15-haswell
#spack load /fdkrhz7 #harfbuzz
#spack load fribidi@1.0.5%gcc@11.2.0 arch=linux-sles15-haswell
#module restore my_r_env

export TMPDIR="/dss/dsshome1/00/ge35xof4/tmp"
export TMP="/dss/dsshome1/00/ge35xof4/tmp"
export TEMP="/dss/dsshome1/00/ge35xof4/tmp"
R -e "tempdir()"
#R -e "install.packages('sf', repos = 'http://cran.us.r-project.org')"
#R -e "install.packages('cleandata', repos = 'http://cran.us.r-project.org')"
#R -e "install.packages('devtools', repos = 'http://cran.us.r-project.org')"
#module save my_r_env

#./run_all.sh

cd $1
time ./train.sh
