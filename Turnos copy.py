from calendar import weekday
from dataclasses import dataclass
from datetime import date, timedelta
from operator import contains
import random

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



def make_shift(n_ppl, turno, posicao):
    people = []
    pre_result = []
    for i in range(n_ppl):
        people.append(Pessoa(turno-1,0))
        pre_result.append(["Operador", str(turno), str(random.randint(0,100))])

    timeframe = daterange(start_date, end_date)
    for single_date in timeframe:
        if getweekday(single_date) == 7:
            pick_rest = list(range(1,7))
            random.shuffle(pick_rest)
            #reset vacation and change turn
            for i in range(n_ppl):
                if people[i].descanso:
                    leftover=pick_rest.pop() if len(pick_rest) != 0 else random.randint(1,7)
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
            if len(pick_rest) > 0:
                i = pick_rest.pop()
                people[i].descanso = people[i].descanso-1
                pre_result[i].append("D")
            for ii in range(n_oper):
                if i != ii:
                    pre_result[ii].append(turn_code)

    return pre_result

def make_shifts(n_oper, posicao):
    pre_result = []
    for i in range(3):
        pre_result +=make_shift(n_oper, i, posicao)
    
    
    return pre_result
 


timeframe = daterange(start_date, end_date)
#fill date
result = "Posição,Grupo,Nome,"



for single_date in timeframe:
        result+=str(single_date)+","
result+="\n"

       
##Make Operators
pre_result = []


pre_result += make_shifts(n_oper, "Operadores")
pre_result += make_shifts(n_auxprod, "Auxiliar de Produção")
pre_result += make_shifts(n_eng, "Engenheiros")
pre_result += make_shifts(n_control, "Controlo de Qualidade")
pre_result += make_shifts(n_arm, "Armazém")
pre_result += make_shifts(n_log, "Logistica")
for line in pre_result:
    result+=",".join(line)+"\n"



with open("result.csv","w") as file:
    file.write(result)