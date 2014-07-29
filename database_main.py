#Written by Shreyes H. Joshi, Princeton University

from database_file3 import *
import timeit

def run():
	#86080984
	#serial_min = int(raw_input('Enter the lower bound serial number (inclusive): '))
	#serial_max = int(raw_input('Enter the upper bound serial number (inclusive): '))
	serial_min = 86080970
	serial_max = 86080970
	global possible_attorneys
	possible_attorneys = serial_max - serial_min + 1.0 #total attorneys possible 
	span = range(serial_min, serial_max + 1) #list spanning possible_attorneys
	traverse(span)
	#info = traverse(span) #collect all data from traverse and write csv files

#code below times the entire program
time_elapsed = timeit.timeit(run, number = 1)
time_per_attorney = time_elapsed/possible_attorneys
print "Time for this run = " + str(time_elapsed) + " seconds"
print "Time elapsed per trademark scanned = " + \
       str(time_per_attorney) + " seconds"