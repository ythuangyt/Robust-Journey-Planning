import argparse
import os
import numpy as np
import ast

parser = argparse.ArgumentParser()
parser.add_argument("--script_name", default='submit.sh')				
parser.add_argument("--logs_folder", default='./logs')	
parser.add_argument("--job_name", default='')		
parser.add_argument("--env", nargs='+', default=["Pendulum-v0"])
parser.add_argument("--optimizer", nargs='+', default=["SGLD"])
parser.add_argument("--thermal_noise", nargs='+', default=["0"])	
parser.add_argument("--action_noise_scale", nargs='+', default=["0"])
parser.add_argument("--action_noise", type=ast.literal_eval)
parser.add_argument("--two_player", type=ast.literal_eval)
args = parser.parse_args()

# If submit script does not exist, create it
if not os.path.isfile(args.script_name):
    with open(args.script_name, 'w') as file:
        file.write(f'''#!/bin/bash

#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=2-00:00:00
#SBATCH --mem-per-cpu=10000

./staskfarm ${{1}}\n''')


for env in args.env:
    for thermal_noise in (args.thermal_noise):
        if args.action_noise:
            for action_noise_scale in (args.action_noise_scale):                      
                folder_name = f'{env}'
                if (args.optimizer == ["SGLD"]):
                    experiment = f'SGLD_thermal_{thermal_noise}/action_{action_noise_scale}'
                    optimizer = 'SGLD'
                else:
                    experiment = f'RMSprop/action_{action_noise_scale}'
                    optimizer = 'RMSprop'
                path = f'{folder_name}/{experiment}'

                if not os.path.isdir(f'{args.logs_folder}/{path}'):
                    os.makedirs(f'{args.logs_folder}/{path}')
                                
                print(path)
              
                command = f'python3.6 main.py --env-name {env} --optimizer {optimizer} --epsilon {thermal_noise} --action_noise True --noise_scale {action_noise_scale} --two_player {args.two_player}'

                experiment_path = f'{args.logs_folder}/{path}/command.txt'
                               
                with open(experiment_path, 'w') as file:
                    file.write(f'{command}\n')
                                
                print(command)

                if not args.job_name:
                    job_name = path
                else:
                    job_name = args.job_name

                os.system(f'sbatch --job-name={job_name} {args.script_name} {experiment_path}')
        else:
            folder_name = f'{env}'
            if (args.optimizer == ['SGLD']):
                experiment = f'SGLD_{thermal_noise}/no_noise'
                optimizer = 'SGLD'
            else:
                experiment = f'RMSprop/no_noise'
                optimizer = 'RMSprop'
            path = f'{folder_name}/{experiment}'

            if not os.path.isdir(f'{args.logs_folder}/{path}'):
                os.makedirs(f'{args.logs_folder}/{path}')

            print(path)

            command = f'python3.6 main.py --env-name {env} --optimizer {optimizer} --epsilon {thermal_noise} --action_noise False --two_player {args.two_player}'
            experiment_path = f'{args.logs_folder}/{path}/command.txt'
            print(experiment_path)
            
            with open(experiment_path, 'w') as file:
                file.write(f'{command}\n')

            print(command)

            if not args.job_name:
                job_name = path
            else:
                job_name = args.job_name

            os.system(f'sbatch --job-name={job_name} {args.script_name} {experiment_path}')

