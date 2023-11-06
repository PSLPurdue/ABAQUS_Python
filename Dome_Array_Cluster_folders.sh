#!/bin/bash
#!/bin/sh
#SBATCH -A aarrieta
#SBATCH --nodes=1 --ntasks=10
#SBATCH --time=3:00:00
#SBATCH -J Dome_Example
#SBATCH -o Dome_Example%j.out
#SBATCH -e Dome_Example%j.out
#SBATCH --mail-user=osorio2@purdue.edu # Destination email address
#SBATCH --mail-type=END,FAIL # Event(s) that triggers email notification (BEGIN,END,FAIL,ALL)
#SBATCH --array 1-9%9 # IMPORTANT! This gives you the paralell runs --> array initial-last%max jobs at a time

# Go where we were when we typed 'squeue'
if [[ -n $SLURM_SUBMIT_DIR ]]; then
	cd $SLURM_SUBMIT_DIR
fi

echo "Simulation had started for ${obj_type} Objects"
echo "Starting in: $(pwd)"

# ------------------------------------------------------
# Load Modules
# ------------------------------------------------------
# Bell: # Use the following line to run Abaqus at Bell (Check account -A)
module load anaconda/2020.11-py38
module load rcac

# Bell: Use the following line to run Abaqus at Bell (Check account -A)
module load intel abaqus/2021
unset SLURM_GTIDS

# ------------------------------------------------------
# Create general directories 
# (Directories for converged and Failed Simulations)
# ------------------------------------------------------

# GENERAL ------------------------------------------------------
inp_folder="inp_files"
if [ ! -d "${inp_folder}" ]; then
  mkdir -p "${inp_folder}"
fi

out_folder="out_files"
if [ ! -d "${out_folder}" ]; then
  mkdir -p "${out_folder}"
fi

# ------------------------------------------------------
# SUCCESS :)!
# ------------------------------------------------------

msg_folder="msg_files"
sta_folder="sta_files"
dat_folder="dat_files"
results_folder="results"

if [ ! -d "${msg_folder}" ]; then
  mkdir -p "${msg_folder}"
fi

if [ ! -d "${sta_folder}" ]; then
  mkdir -p "${sta_folder}"
fi

if [ ! -d "${dat_folder}" ]; then
  mkdir -p "${dat_folder}"
fi

if [ ! -d "${results_folder}" ]; then
  mkdir -p "${results_folder}"
fi

# ------------------------------------------------------
# FAIL :(!
# ------------------------------------------------------
fail_simulations="fail_simulations"

if [ ! -d "${fail_simulations}" ]; then
  mkdir -p "${fail_simulations}"
fi

# ------------------------------------------------------
# Loop over cases
# ------------------------------------------------------
echo "Start Loop"

n=$SLURM_ARRAY_TASK_ID # Get n simulation value from array

# Make temporary directory
workingdir="Case_${n}"
mkdir -p "${workingdir}"

# Copy files to directory
cp common/Dome_Geometry_${n}.inp $workingdir  # INP_Files

cd $workingdir

# ------------------------------------------------------------------------------------------------------------
# Change as required
# ------------------------------------------------------------------------------------------------------------

# Submmit Job with out CAE license
job_name="Dome_Geometry_${n}"
inp_name="Dome_Geometry_${n}"

abaqus interactive job=${job_name} inp=${inp_name}.inp cpus=$SLURM_NTASKS scratch=$PWD

# ------------------------------------------------------------------------------------------------------------
# Move files
# ------------------------------------------------------------------------------------------------------------
sim_completed="0" # Initialized to 0 and change to 1 if the analysis is successful

out_files="*.out"

dat_files="*.dat"
sta_files="*.sta"
msg_files="*.msg"
inp_files="*.inp"
odb_files="*.odb"      # Results files

if [ -f *.sta ]; then
  sim_completed=$(grep -c 'SUCCESSFULLY' *.sta)
  cp $inp_files -t ../$inp_folder
  
  if [ $sim_completed -eq 0 ]; then
    echo "The analysis was not successful"
    cp $msg_files -t ../$fail_simulations
    cp $sta_files -t ../$fail_simulations
    cp $dat_files -t ../$fail_simulations
    cp $odb_files -t ../$fail_simulations
    
    # Back to the main folder
    cd ..

    # ------------------------------------------------------
    # Remove working directory
    # ------------------------------------------------------
    rm -rf "${workingdir}"/*
    rm -rf "${workingdir}"
  else
    echo "The analysis was successful"
    cp $msg_files -t ../$msg_folder
    cp $sta_files -t ../$sta_folder
    cp $dat_files -t ../$dat_folder
    cp $out_files -t ../$out_folder
  
    cp $odb_files -t ../$results_folder

    # Back to the main folder
    cd ..

    # ------------------------------------------------------
    # Remove working directory
    # ------------------------------------------------------
    rm -rf "${workingdir}"/*
    rm -rf "${workingdir}"
  fi

else
  echo "Error in simulation files ${result}"
fi

cp $out_files -t $out_folder
rm $out_files