"""
 Copyright 2022 github.com/P1514
 
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 
      http://www.apache.org/licenses/LICENSE-2.0
 
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 """

from calendar import weekday
from dataclasses import dataclass
from datetime import date, timedelta
import math
from operator import contains
import random
import sys
from time import sleep
from os.path import exists

#inputs
#n_oper = 11
#n_auxprod=6
#n_eng=5
#n_control=3
#n_arm=2
#n_log=3

efficiency = False

positions = dict()
positions["Operador"] = 9
positions["Auxiliar de Produção"] = 5
positions["Engenheiros"] = 4
positions["Controlo"] = 2
positions["Armazem"] = 1
positions["Logistica"] = 2

#WARNING: START DATE MUST BE A SUNDAY
start_date = date(2022, 4, 3)
end_date = date(2022, 12, 31)

#endinputs dont change anything else

load_file=False


result = {}
@dataclass
class Shift:
    rests: int
    workdays: int
    stop_days: list


    def __post_init__(self):
        if self.workdays + len(self.stop_days) > 7:
            raise NotImplementedError("Multiweek work schedule not supported")
            

#Shift Definition
shifts = []
shifts.append(Shift(1,6,[7]))
shifts.append(Shift(1,6,[7]))
shifts.append(Shift(0,5,[6,7]))
#End Shift Definition


@dataclass
class Pessoa:
    turno: int
    descanso: int

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def getweekday(single_date):
    return single_date.isocalendar()[2]

def make_shift(n_ppl, nomes, grupo, posicao):
    people = []
    pre_result = []
    for i in range(n_ppl):
        people.append(Pessoa(grupo-1,0))
        pre_result.append([posicao, str(grupo), str(nomes[i])])
    timeframe = daterange(start_date, end_date)
    for single_date in timeframe:
        if getweekday(single_date) == 7:
            pick_rest = list(range(1,7))
            random.shuffle(pick_rest)
            #reset vacation and change turn
            for i in range(n_ppl):
                if people[i].descanso:
                    if len(pick_rest) != 0:
                        leftover=pick_rest.pop() 
                    else:
                        pick_rest = list(range(1,7))
                        random.shuffle(pick_rest)
                        leftover=pick_rest.pop()
                    if "D" in pre_result[i][-leftover]:
                        old_leftover= leftover
                        leftover=pick_rest.pop() if len(pick_rest) != 0 else random.randint(1,7)
                        pick_rest.append(old_leftover)
                    pre_result[i][-leftover] ="D"
                
                turn_code=(people[i].turno+1)%3
                people[i].turno=turn_code
                turn_code= "M" if turn_code == 0 else "T" if turn_code == 1 else "N"
                people[i].descanso=1 if people[i].turno != 2 else 0
                pre_result[i].append("D")

            pick_rest = list(range(n_ppl))
            random.shuffle(pick_rest)
        elif getweekday(single_date) == 6 and people[0].turno == 2:
            for i in range(n_ppl):
                pre_result[i].append("D")
            continue

        else:
            i=-1
            if len(pick_rest) > 0 and people[0].turno != 2:
                i = pick_rest.pop()
                people[i].descanso = people[i].descanso-1
                pre_result[i].append("D")
            for ii in range(n_ppl):
                if i != ii:
                    pre_result[ii].append(turn_code)

    return pre_result

def make_shifts(nworkers, position):
    pre_result = []
    workers = [[],[],[]]
    for nome, grupo in names[position]:
        workers[grupo].append(nome)
    for i in range(len(shifts)):
        pre_result += make_shift(nworkers,workers[i], i, position)
    
    return pre_result
 
def required_people_per_shift(positions):
    fill_coefficient = 0
    for shift in shifts:
        fill_coefficient = max(fill_coefficient, shift.rests / shift.workdays)
    for position, min_workers in positions.items():
        #Missing Efficiency Here
        positions[position] = min_workers + math.ceil(min_workers * fill_coefficient)

def make_people():
    names = {}
    for position, nworkers in positions.items():
        names[position] = []
        for grupo in range(len(shifts)):
            for i in range(nworkers):
                names[position].append([random.randint(0,100), grupo])
    return names


required_people_per_shift(positions)

if getweekday(start_date) != 7:
    print("O PRIMEIRO DIA TEM DE SER UM DOMINGO")
    sleep(5)
    exit(1)



timeframe = daterange(start_date, end_date)
#fill date
result = "Posição,Grupo,Nome,"



for single_date in timeframe:
        result+=str(single_date)+","
result+="\n"

       
#Make Operators
pre_result = []

names = make_people()

for position, nworkers in positions.items():
    pre_result += make_shifts(nworkers, position)

for line in pre_result:
    result+=",".join(line)+"\n"


file_name = "turnos_novo.csv" if load_file else "turnos.csv"
with open(file_name,"w") as file:
    file.write(result)