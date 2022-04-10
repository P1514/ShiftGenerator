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
import pandas as pd

@dataclass
class Shift:
    name: int
    rests: int
    workdays: int
    stop_days: list
    code: str


    def __post_init__(self):
        if self.workdays + len(self.stop_days) > 7:
            raise NotImplementedError("Multiweek work schedule not supported")
            
@dataclass
class People:
    name: str
    position: str
    cur_shift: int
    worklist: list = list


    def __post_init__(self):
        self.worklist = []

@dataclass
class Position:
    name: str
    shifts: list
    min_people: int
    required_people: int = 0


#NOT USED YET
efficiency = False


#Positions
positions = list()
positions.append(Position("Operador", [0,1,2], 9))
positions.append(Position("Auxiliar de Produção",[0,1,2],5))
positions.append(Position("Engenheiros",[0,1,2],4))
positions.append(Position("Controlo",[0,1,2],2))
positions.append(Position("Armazem",[0,1,2],1))
positions.append(Position("Logistica",[0,1,2],2))
#End Positions


#WARNING: START DATE MUST BE A SUNDAY
start_date = date(2022, 4, 11)
end_date = date(2022, 12, 31)

#endinputs dont change anything else

load_file=False


#Shift Definition
shifts = []
shifts.append(Shift(0,1,6,[7], "M"))
shifts.append(Shift(1, 1,6,[7], "T"))
shifts.append(Shift(2, 0,5,[6,7], "N"))
#End Shift Definition


def daterange(start_date, end_date, step = 7, start = 7):
    for n in range(start, int((end_date - start_date).days),step):
        yield start_date + timedelta(n)

def getweekday(single_date):
    return single_date.isocalendar()[2]

def assign_people_to_shift(workers, position):
    for worker in workers:
        worker.cur_shift = (worker.cur_shift+1)%len(position.shifts)

def get_possible_rest_days(stop_days):
    rest_days = list(range(1,8))
    random.shuffle(rest_days)
    for day in stop_days:
        rest_days.remove(day)
    return rest_days

def get_current_shift_workers(workers, shift):
    shift_workers = list()
    for worker in workers:
        if worker.cur_shift == shift:
            shift_workers.append(worker)

    return shift_workers

def make_shift(workers, position):
    timeframe = daterange(start_date, end_date)
    for single_date in timeframe:
        assign_people_to_shift(workers, position)
        for shift in position.shifts:
            shift = shifts[shift]
            shift_code = shift.code
            available_rests = get_possible_rest_days(shift.stop_days)
            shift_workers = get_current_shift_workers(workers, shift.name)
            for worker in shift_workers:
                worklist = worker.worklist
                worklist += [shift_code]*7
                for stop_day in shift.stop_days:
                    worklist[(-7+stop_day-1)]= "D"

                for i in range(shift.rests):
                    if len(available_rests) == 0:
                        available_rests = get_possible_rest_days(shift.stop_days)
                    worklist[-7+available_rests.pop()-1] = "D"


def required_people_per_shift(positions):
    fill_coefficient = 0
    for shift in shifts:
        fill_coefficient = max(fill_coefficient, shift.rests / shift.workdays)
    for position in positions:
        #Missing Efficiency Here
        position.required_people = position.min_people + math.ceil(position.min_people * fill_coefficient)

def make_people():
    people = {}
    for position in positions:
        people[position.name] = []
        for shift in range(len(shifts)):
            for i in range(position.required_people):
                people[position.name].append(People(random.randint(0,100), position.name, shift))
    return people


#Read Excel Data
open("")

sys.exit(1)
#Finish Read Excel Data


required_people_per_shift(positions)

if getweekday(start_date) != 1:
    print("O PRIMEIRO DIA TEM DE SER UMA Segunda")
    sleep(5)
    exit(1)



timeframe = daterange(start_date, end_date, 1, 0)
#fill date
header = ["Posição","Nome"]

for single_date in timeframe:
    header.append(str(single_date))

people = make_people()

for position in positions:
    make_shift(people[position.name], position)


csv_result = ",".join(header)
csv_result += "\n"

for position, workers in people.items():
    for worker in workers:
        csv_result += f'{position},'
        csv_result += f'{worker.name},'
        csv_result += ",".join(worker.worklist)
        csv_result += "\n"

file_name = "turnos_novo.csv" if load_file else "turnos.csv"
with open(file_name,"w") as file:
    file.write(csv_result)