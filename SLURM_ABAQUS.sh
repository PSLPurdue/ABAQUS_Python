#!/bin/bash
#!/bin/sh
#SBATCH -A aarrieta                     # ACCOUNT NAME
#SBATCH --nodes=1 --ntasks=10           # NUMBER OF CPUS USED TO RUN THE JOB. CAN BE CALL USING $SLURM_NTASKS
#SBATCH --time=5:00:00                  # TOTAL TIME (IN HOURS!) THE JOB WOULD RUN (IT WOULD STOP RUNNING IF YOU REACH THE TIME LIMIT)
#SBATCH -J bash_example                 # CHANGE TO THE NAME YOU LIKE. THIS NAME WOULD APPEAR WHEN "squeue -u $USER" IS CALL IN THE TERMINAL
#SBATCH -o bash_example%j.out           # OUTPUT FILE NAME
#SBATCH -e bash_example%j.out           # ERROR FILE NAME
#SBATCH --mail-user=osorio2@purdue.edu  # DESTINATION EMAIL ADRESS
#SBATCH --mail-type=END,FAIL            # Event(s) that triggers email notification (BEGIN,END,FAIL,ALL)

#------------------------------------------------------------------------------------------------------
# LOAD MODULES
#------------------------------------------------------------------------------------------------------
# module load abaqus/2018               # HALSTEAD/BROWN CLUSTER
module load intel abaqus/2020           # BELL CLUSTER
unset SLURM_GTIDS

#------------------------------------------------------------------------------------------------------
# RUN JOB (ABAQUS)
#------------------------------------------------------------------------------------------------------
# RUN JOB WITH .INP FILE (THE NAME SHOULD MATCH THE .INP FILE YOU UPLOAD)
# ALL FILES NEED TO BE IN THE SAME FOLDER
job_name="FILE_NAME"
inp_name="FILE_NAME"

abaqus interactive job=${job_name} inp=${inp_name}.inp cpus=$SLURM_NTASKS scratch=$PWD

# RUN JOB WITH PYTHON SCRIPT
abaqus cae noGUI=FILE_NAME.py

# PRINT A MESSAGE ON THE .out FILE WHEN THE JOB IS FINISH
echo "JOB IS DONE!"