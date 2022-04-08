"""
 Copyright 2022 Guilherme Gois
 
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
from operator import contains
import random
from time import sleep
from os.path import exists

#inputs
n_oper = 11
n_auxprod=6
n_eng=5
n_control=3
n_arm=2
n_log=3

min_oper= 9
min_auxprod= 5
min_eng= 4
min_control= 2
min_arm= 1
min_log= 2

#WARNING: START DATE MUST BE A SUNDAY
start_date = date(2022, 4, 3)
end_date = date(2022, 12, 31)

#endinputs dont change anything else

load_file=False


result = {}
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

def make_shifts(n_ppl, nomes, posicao):
    pre_result = []
    nomes_grupo = [[],[],[]]
    for nome, grupo in nomes:
        nomes_grupo[grupo].append(nome)
    for i in range(3):
        pre_result +=make_shift(n_ppl,nomes_grupo[i], i, posicao)
    
    return pre_result
 

def make_people(n_oper, n_auxprod, n_eng, n_control, n_arm, n_log):
    nomes = {}
    nomes['oper'] = []
    nomes['aux'] = []
    nomes['eng'] = []
    nomes['control'] = []
    nomes['arm'] = []
    nomes['log'] = []
    if not exists("result.csv"):
        for grupo in range(3):
            for i in range(n_oper):
                nomes['oper'].append([random.randint(0,100), grupo])
            for i in range(n_auxprod):
                nomes['aux'].append([random.randint(0,100), grupo])
            for i in range(n_eng):
                nomes['eng'].append([random.randint(0,100), grupo])  
            for i in range(n_control):
                nomes['control'].append([random.randint(0,100), grupo])            
            for i in range(n_arm):
                nomes['arm'].append([random.randint(0,100), grupo])           
            for i in range(n_log):
                nomes['log'].append([random.randint(0,100), grupo])
    else:
        with open("turnos.csv") as file:
            pass


    return nomes

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

       
##Make Operators
pre_result = []

nomes = make_people(n_oper, n_auxprod, n_eng, n_control, n_arm, n_log)


pre_result += make_shifts(n_oper, nomes['oper'], "Operadores")
pre_result += make_shifts(n_auxprod, nomes['aux'], "Auxiliar de Produção")
pre_result += make_shifts(n_eng, nomes['eng'], "Engenheiros")
pre_result += make_shifts(n_control,nomes['control'], "Controlo de Qualidade")
pre_result += make_shifts(n_arm,nomes['arm'],"Armazém")
pre_result += make_shifts(n_log,nomes['log'],"Logistica")
for line in pre_result:
    result+=",".join(line)+"\n"


file_name = "turnos_novo.csv" if load_file else "turnos.csv"
with open(file_name,"w") as file:
    file.write(result)