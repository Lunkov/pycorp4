#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

class CalculatorDB():
  def __init__ (self, verbose = 0):
    self.__verbose = verbose

  def calcTable(self, cntRows):
    return 0

  def calcIndex(self, cntRows):
    # https://docs.microsoft.com/ru-ru/sql/relational-databases/databases/estimate-the-size-of-a-clustered-index?view=sql-server-ver15
    # Num_Rows = число строк в таблице
    # Num_Cols = общее количество столбцов (фиксированной и переменной ширины)
    # Fixed_Data_Size = общий размер в байтах всех ключевых столбцов фиксированной длины
    # Num_Variable_Cols = количество включенных столбцов переменной длины
    # Max_Var_Size = максимальный размер в байтах всех столбцов переменной длины
    return 0
  
  def calcDB(self, cntRows):
    return 0
