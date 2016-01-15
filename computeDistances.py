#!/bin/python                                                                                                                                                           
                                                                                                                                                                        
import csv                                                                                                                                                              
import sys                                                                                                                                                              
import json                                                                                                                                                             
import math                 
import osr
from multiprocessing import Pool                                                                                                                                        
from osrm import OSRM                                                                                                                                                   
from progressbar import ProgressBar, Percentage, ETA                                                                                                                    
                                                                                                                                                                        
osrm = OSRM("/root/osrm-c/build/libosrm_c.so.0.2.0")                                                                                                                       
#osrm.query([[44.6816169436,4.26732915504],[44.790242504,4.22572356575]])                                                                                               
                                                                                                                                                                        
outputFilename="test.csv"                                                                                                                    
# routes to query will be splitted for estimating the total computation time                                                                                            
chunksSize=1000                                                                                                                                                         
# nb of processors to use in parallel                                                                                                                                   
npProcessors=2    
# max euclidean distance in meters for considering a couple of municipalities
maxDistance = 100*1000

# projections init
sr2154 = osr.SpatialReference()
sr2154.ImportFromEPSG(2154) # Lambert93
sr4326 = osr.SpatialReference()
sr4326.ImportFromEPSG(4326)  #wgs84
srTransTo4326 = osr.CoordinateTransformation(sr2154,sr4326)

# compute euclidian distance in meters with projection Lambert93
def euclidianDistance(fromCoords, toCoords):
  return math.hypot(fromCoords[0]-toCoords[0],fromCoords[1]-toCoords[1])
                                                                                                                                                           
def processALine(line):
  '''
  Computes the distance and the travel time for two points.
  line: array containing origin id, origin lat, origin lon, dest id, dest lat, dest lon.
  returns: array containing origin id, dest id, travel time in seconds, distance in km
  '''
  print(line)
  result = osrm.query([map(float,line[1:3]),map(float,line[4:])])
  try:
    data = json.loads(result)
  except ValueError:
    print "Error with route from "+str(origin)+" to "+str(dest)
    return [line[0],line[3],None,None]
  if u'route_summary' not in data:
    return [line[0],line[3],None,None]
  else:
    seconds = data[u'route_summary'][u'total_time']
    distance = data[u'route_summary'][u'total_distance']    
    if u'alternative_summaries' in data:
      for alt_route in data[u'alternative_summaries']:
        if shortest:
          if alt_route[u'total_distance'] < distance:
            seconds = alt_route[u'total_time']
            distance = alt_route[u'total_distance']
        elif alt_route[u'total_time'] < seconds:
          seconds = alt_route[u'total_time']
          distance = alt_route[u'total_distance']
    return [line[0],line[3],seconds,float(distance)/1000]

if __name__ == "__main__":
  shortest=True
  if shortest:
    print 'Computing the *shortest* path. If you want the fastest, please set the variable "shortest" to False'
  else:
    print 'Computing the *fastest* path. If you want the shortest, please set the variable "shortest" to True'
  with open(outputFilename, 'wb') as outputFile:
    distances=[]
    output = csv.writer(outputFile,delimiter=";")
    output.writerow(["from","to","seconds","km"])
    # read input data
    with open('communes-plus-20140630.csv','rb') as f:
        f.readline() # skip headers
        data=[]
        for row in csv.reader(f):
            if row[0].startswith('1501'):
                #if row[0]=="76095": row[7]="563412"; row[8]="6929988" # fix missing data in communes-plus-20140630
                x,y=[int(row[7])*100, int(row[8])*100] # fix for old x/y coordinates in hectometers. Should be fixed in last versions of GeoFLA
                center = srTransTo4326.TransformPoint(x,y)
                data.append([row[0],float(center[0]),float(center[1]),row[1],x,y])
    pool = Pool(processes=npProcessors)
    nbDistances = len(data) * (len(data) - 1)
    pb = ProgressBar(widgets=[Percentage(), ETA()],maxval=max(1,math.ceil(nbDistances/chunksSize))).start()
    chunk=[]
    # loop on municipalities
    for i,munFrom in enumerate(data[:3]):
        for j,munDest in enumerate(data[:3]):
            if i != j :
                # compute distance
                distance = euclidianDistance(munFrom[4:6],munDest[4:6])
                if distance<maxDistance:
                    # add the current couple to the list of chunks to process
                    chunk.append([munFrom[0],munFrom[2],munFrom[1],munDest[0],munDest[2],munDest[1]])
                    if len(chunk)==chunksSize:
                        # process the chunk
                        for result in pool.map(processALine, chunk):
                            output.writerow(result)
                        pb.update(pb.currval+1)
                        # and reset for the next one
                        chunk=[]
    # processing remaining chunks
    for result in pool.map(processALine, chunk):
        output.writerow(result)
    pb.finish() 

