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
from cmath import nan
from dataclasses import dataclass
from datetime import date, timedelta
import math
from operator import contains
import random
import sys
from time import sleep
from os.path import exists
import pandas as pd
import xlsxwriter

@dataclass
class Shift:
    name: int
    stop_days: list
    code: str
    rests: int = 0
    workdays: int = 0

    def __post_init__(self):
        self.stop_days = list(map(int, str(self.stop_days).split(",")))

        if self.workdays + len(self.stop_days) > 7:
            raise NotImplementedError("Multiweek work schedule not supported")

        self.rests = 2 - len(self.stop_days)
        self.workdays = 7 - len(self.stop_days)
            
@dataclass
class People:
    name: str
    position: str
    cur_shift: int
    worklist: list = list
    double_rest: int = 0
    cur_rest: int = 0


    def __post_init__(self):
        self.worklist = []

@dataclass
class Position:
    name: str
    shifts: list
    min_people: int
    required_people: int = 0

    def __post_init__(self):
        parsed_shifts = []
        for shift_code in self.shifts.split(","):
            for shift in shifts:
                if shift.code == shift_code:
                    parsed_shifts.append(shift.name)
                    break
        self.shifts = parsed_shifts
            

#NOT USED YET
efficiency = False

load_file=False

shifts = list()
positions = list()

def daterange(start_date, end_date, step = 7, start = 7):
    for n in range(start, int((end_date - start_date).days + step),step):
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
        day_after = ((day + 1) % 7 )
        day_before = 7 if day == 1 else ((day - 1) % 7)
        if day_after in rest_days:
            rest_days.remove(day_after)
            rest_days.insert(0, day_after)
        
        if day_before in rest_days:
            rest_days.remove(day_before)
            rest_days.insert(0, day_before)

    return rest_days

def get_current_shift_workers(workers, shift):
    shift_workers = list()
    for worker in workers:
        if worker.cur_shift == shift:
            shift_workers.append(worker)

    return shift_workers

def check_if_consecutive(stop_days, rest):
    for stop_day in stop_days:
        if stop_day - 1 == rest or stop_day + 1 == rest or (stop_day == 7 and rest == 1) or (stop_day == 1 and rest == 7) :
            return True
    return False

def get_double_rest(workers):
    double_rest = sys.maxsize
    for worker in workers:
        double_rest = min(double_rest, worker.double_rest)
    
    return double_rest

def make_shift(workers, position):
    timeframe = daterange(start_date, end_date)
    for single_date in timeframe:
        assign_people_to_shift(workers, position)
        for shift in position.shifts:
            shift = shifts[shift]
            shift_code = shift.code
            shift_workers = get_current_shift_workers(workers, shift.name)
            # Give Stop Days
            for worker in shift_workers:
                worklist = worker.worklist
                worklist += [shift_code]*7
                for stop_day in shift.stop_days:
                    worklist[(-7+stop_day-1)]= "D"
            # Give Stop Days

            while (len(shift_workers) > 0):
                available_rests = get_possible_rest_days(shift.stop_days)
            
                for day in available_rests:
                    for worker in shift_workers:
                        if worker.cur_rest == shift.rests:
                            worker.cur_rest = 0
                            shift_workers.remove(worker)
                            continue
                        double_rest = get_double_rest(shift_workers)
                        if check_if_consecutive(shift.stop_days, day) :
                            if double_rest == worker.double_rest:
                                worker.double_rest = worker.double_rest + 1
                            else:
                                continue
                        
                        worker.worklist[-7+day-1] = "D"
                        worker.cur_rest = worker.cur_rest + 1
                        break


def required_people_per_shift(positions):
    fill_coefficient = 0
    for shift in shifts:
        fill_coefficient = max(fill_coefficient, shift.rests / shift.workdays)
    for position in positions:
        #Missing Efficiency Here
        position.required_people = position.min_people + math.ceil(position.min_people * fill_coefficient)

def make_people():
    worker_number = 1
    people = {}
    for position in positions:
        people[position.name] = []
        for shift in range(len(shifts)):
            for i in range(position.required_people):
                people[position.name].append(People(worker_number, position.name, shift))
                worker_number = worker_number + 1
    return people

def add_position(positions, position, shift, workers):
    for pos in positions:
        if pos.name == position:
            pos.min_people = pos.min_people + workers
            return
    positions.append(Position(position, shift, workers))


#Read Excel Data
inputs =  pd.read_excel('Planeamento Turnos - fich gui.xlsx', None)
conf = inputs["Configuração"]
start_date = conf["Inicio"][0]
end_date = conf["Fim"][0]

i = 0
for shift, rest in zip(conf["Codigo Turnos"],conf["Descanço"]):
    if pd.isna(shift) or pd.isna(rest):
        break
    shifts.append(Shift(i,rest, shift))
    i = i + 1

for position, min_workers, n_equips, shift in zip(conf["Nome"],conf["Minimo"],conf["Nº Equipamentos"],conf["Turnos"]):
    add_position(positions, position, shift, min_workers*n_equips)

#Finish Read Excel Data


required_people_per_shift(positions)

start_date_wd = getweekday(start_date)
end_date_wd = getweekday(end_date)


if start_date_wd != 1:
    start_date = start_date - timedelta(start_date_wd - 1)

if end_date_wd != 7:
    end_date = end_date + timedelta(7 - end_date_wd)


timeframe = daterange(start_date, end_date, 1, 0)
#fill date
header = ["Posição","Nome"]

for single_date in timeframe:
    header.append(single_date)

people = make_people()

for position in positions:
    make_shift(people[position.name], position)

result = []
for position, workers in people.items():
    for worker in workers:
        entry = [position, worker.name] 
        entry += worker.worklist
        result.append(entry)

#file_name = "turnos_novo.csv" if load_file else "turnos.csv"
#with open(file_name,"w") as file:
#    file.write(csv_result)
size_header = math.floor((len(header) - 2) / 7) 
header = header[0:size_header*7 + 2]

df = pd.DataFrame(result,columns=header)

writer = pd.ExcelWriter("Resultado Turnos.xlsx", engine='xlsxwriter')

df.to_excel(writer, sheet_name='Sheet1')

# Get the xlsxwriter workbook and worksheet objects.
workbook  = writer.book
worksheet = writer.sheets['Sheet1']
format1 = workbook.add_format({'bg_color': '#D9D9D9',
                               'font_color': '#000000'})
format2 = workbook.add_format({'bg_color': '#A6A6A6',
                               'font_color': '#000000'})
# Get the dimensions of the dataframe.
(max_row, max_col) = df.shape

# Apply a conditional format to the required cell range.
worksheet.conditional_format(0, 0, max_row, max_col,
                             {'type': 'formula',
                             'criteria': '=WEEKDAY(A$1)=1',
                             'format':   format2})
worksheet.conditional_format(0, 0, max_row, max_col,
                             {'type': 'formula',
                             'criteria': '=AND(WEEKDAY(A$1)<>1,A1="D")',
                             'format':   format1})


writer.save()

print("Done")