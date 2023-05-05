import configparser as cfg
import os
from time import sleep

import pandas as pd
import colorama

colorama.just_fix_windows_console()

class MasterPlateMaker():

    colors = {'PURPLE': '\033[95m',
              'CYAN': '\033[96m',
              'DARKCYAN': '\033[36m',
              'BLUE': '\033[94m',
              'GREEN': '\033[92m',
              'YELLOW': '\033[93m',
              'RED': '\033[91m',
              'BOLD': '\033[1m',
              'UNDERLINE': '\033[4m',
              'END': '\033[0m',
              'NONE': ''}

    required_fields = ['NAME_CSV', \
                       'ROW_PLATE1_NUM',\
                       'COL_PLATE1_NUM', \
                       'ROWS_BETWEEN_PLATES', \
                       'ROW_SAMPLE_P1_A1', \
                       'COL_SAMPLE_P1_A1', \
                       'ROWS_PLATE', \
                       'COLS_PLATE', \
                       'CLEAR_TERMINAL', \
                       'RESUME_PROGRAM', \
                       'RESUME_ROW', \
                       'RESUME_COL', \
                       'RESUME_PLATE']
    
    row_letter_dict =  {1:  'A',
                        2:  'B',
                        3:  'C',
                        4:  'D',
                        5:  'E',
                        6:  'F',
                        7:  'G',
                        8:  'H',
                        9:  'I',
                        10: 'J',
                        11: 'K',
                        12: 'L',
                        13: 'M',
                        14: 'N',
                        15: 'O',
                        16: 'P',
                        }

    def __init__(self):
        self.cfg = []
        self.validateConfig()

        self.plates_found = 0
        self.current_row = 0
        self.current_col = 0
        self.current_plate = 0
        self.well_id = ''
        self.sample_id = ''

        fn = self.cfg['FILE_NAME']
        res = self.cfg['RESUME']
        ff = self.cfg['FILE_FORMAT']
        pf = self.cfg['PROGRAM_FORMAT']

        if res.getboolean('RESUME_PROGRAM'):
            self.current_row = int(res['RESUME_ROW'])
            self.current_col = int(res['RESUME_COL'])
            self.current_plate = int(res['RESUME_PLATE'])

        self.csv_name = fn['NAME_CSV']

        self.plate_id_row = int(ff['ROW_PLATE1_NUM'])
        self.plate_id_col = int(ff['COL_PLATE1_NUM'])
        self.plate_offset = int(ff['ROWS_BETWEEN_PLATES'])
        self.row_offset = int(ff['ROW_SAMPLE_P1_A1'])
        self.col_offset = int(ff['COL_SAMPLE_P1_A1'])
        self.plate_rows = int(ff['ROWS_PLATE'])
        self.plate_cols = int(ff['COLS_PLATE'])

        self.clear_term = pf.getboolean('CLEAR_TERMINAL')
        self.color_p = self.colors[pf['COLOR_PLATE']]
        self.color_w = self.colors[pf['COLOR_WELL']]
        self.color_s = self.colors[pf['COLOR_SAMPLE']]

    def run(self):
        "Execute program."
        self.loadCSV()
        self.numPlates()
        while(1):
            self.wellID()
            self.sampleID()
            self.terminateNull()
            self.printToTerm()
            self.nextWell()

    def terminateNull(self):
        if pd.isnull(self.sample_id):
            self.sample_id= 'NO SAMPLE - TERMINATING'
            self.printToTerm()
            exit()

    def loadCSV(self):
        'Loads the identified CSV file as a DataFrame'
        self.master_plate = pd.read_csv(self.csv_name, header=None, index_col=False) 

    def nextWell(self):
        'Advance the indices for row, col, plate'
        self.current_col += 1
        if self.current_col == self.plate_cols:
            self.current_col = 0
            self.current_row += 1
            if self.current_row == self.plate_rows:
                self.current_plate += 1
                self.current_row = 0
    
    def numPlates(self):
        "Discovers the number of `PLATE#` entries present the master plate CSV."
        search_plate = 1
        plates_found = 0
        row = self.plate_id_row
        col = self.plate_id_col
        max_rows = self.master_plate.iloc[:,self.plate_id_col].size

        while(search_plate):
            search_plate = 0
            if self.master_plate.iloc[row, col].find('PLATE') == 0:
                plates_found += 1
                search_plate = 1
            row += self.plate_offset
            if row > max_rows:
                search_plate = 0
        self.plates_found = plates_found

    def printToTerm(self):
        input('Plate {}{}\033[0m - Well {}{}\033[0m - {}Sample: {}\033[0m   (Press Enter to advance)'.format(self.color_p,self.current_plate + 1,self.color_w, self.well_id, self.color_s,self.sample_id)) 
        sleep(0.25)
        if self.clear_term:
            print(chr(27) + "[2J")

    def sampleID(self):
        'Identify current sample ID.'
        row_global = self.row_offset + self.current_plate * self.plate_offset + self.current_row
        col_global = self.col_offset + self.current_col
        self.sample_id = self.master_plate.iloc[row_global, col_global]

    def wellID(self):
        'Identify current well ID.'
        row_key = self.current_row + 1
        col_num = self.current_col + 1
        self.well_id = self.row_letter_dict[row_key] + str(col_num)

    def validateConfig(self):
        self.cfg = cfg.ConfigParser()
        self.cfg.read('config.ini')
        all_entries = [entry.upper() for section in self.cfg.sections() for entry in self.cfg[section]]

        if not set(self.required_fields).issubset(set(all_entries)):
            raise KeyError('config.ini is missing required fields. All the following must be present: {} . These were the fields found: {}'.format(self.required_fields, all_entries))