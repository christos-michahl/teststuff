#!/usr/bin/env python
# -*- coding: utf-8 -*-
import par2
import par3
import math
from PIL import Image
#import osgeo
import numpy as np
import time
from mpi4py import MPI
import rasterio
import sys

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
# Dasygenis NOTE: REQUIRED LIBRARIES:
'''
pt-get install libgdal-dev libgdal1h
apt-get install python3-gdal


pip3 install image
pip3 install numpy

pip3 install  --global-option=build_endxt --global-option="-I/usr/include/gdal"  GDAL==1.10.0


pip3 install rasterio
pip3 install mpi4py #for windows u need  to first install the 2 files form this link https://www.microsoft.com/en-us/download/confirmation.aspx?id=56511
'''


#when outputflag=1 the k coefficient is calculated.To skip the calculations outputflag must me 0 
outputflag=1
comparestring='Grass_x_cord_675_and_y_cord_341.tif'

#both arrays save the output of the algorithm and are later used in the creation of the tiff files
outpt = [[[0 for z in range(3142)]for y in range(2255)] for x in range(1)]  
outputarray=np.array(outpt)
outsingle=np.array(outpt)

#the following array is used to save the cummulative viewshed
outputarray=outputarray.astype(np.int32)

#the following array is used to save the viewshed analysis of a single cell
outsingle=outsingle.astype(np.int32)

def main():

	erflag=0
	#checking if there is any input
	if len(sys.argv)<=1:
		erflag=7
	#checking if the input for the first and second valiable are one integer each or two integers in a format like "1-10"
	elif (sys.argv[1].find('-') != -1): 
		spot=sys.argv[1].find('-')
		x=[]
		x=sys.argv[1]
		x1= x[:spot]
		x2= x[spot+1:]
		try:
			x1=int(x1)	
		except:
  			erflag=1

		try:
			x2=int(x2)	
			x2+=1
		except:
  			erflag=1

	else:
		try:
			x1=int(sys.argv[1])	
			x2=x1
			x2+=1
		except:
  			erflag=1

	#checking if the input for the third valiable is an integer or two integers in a format like "1-10"
	#alternatevely it checks if the variable contains a "." and considers it an input file
	if  len(sys.argv)>2:

		if (sys.argv[2].find('-') != -1) :
			spot=sys.argv[2].find('-')
			y=[]
			y=sys.argv[2]
			y1= y[:spot]
			y2= y[spot+1:]
			try:
				y1=int(y1)	
			except:
  				erflag=1

			try:
				y2=int(y2)	
				y2+=1
			except:
	  			erflag=1

		else:
			try:
				y1=int(sys.argv[2])	
				y2=y1
				y2+=1
			except:
  				erflag=1
	else:
		erflag=7
	
	startx=0
	starty=0
	endx=3140
	endy=2254
	#if no input files are given the default file names are the following
	dsm='DSM_Test.tif'
	point="Points_applied_to_DSM_and_Reference_from_row_1_to_2255.txt"
	if len( sys.argv)>=4 and erflag==0:

		spot=sys.argv[3].find('.')
		if (spot != -1): 
			dsm=sys.argv[3]
	
			if len( sys.argv)==5:
				point=sys.argv[4]
				
				if sys.argv[4].find('.')==-1:
						erflag=5

		elif sys.argv[3].find('-')!=-1:
			x=[]
			x=sys.argv[3]
			spot=sys.argv[3].find('-')
			startx= x[:spot]
			endx= x[spot+1:]


			try:
				startx=int(startx)
			except:
  				erflag=3

			try:
				endx=int(endx)
				endx+=1
			except:
  				erflag=3
			if len( sys.argv)>4:
				spot=sys.argv[4].find('-')
				y=[]
				y=sys.argv[4]
				starty= y[:spot]
				endy= y[spot+1:]
				try:
					starty=int(starty)
				except:
  					erflag=3

				try:
					endy=int(endy)
					endy+=1
				except:
  					erflag=3
			else:
				erflag=8
			if len( sys.argv)==6:
				dsm=sys.argv[5]
				if len( sys.argv)==7:
					point=sys.argv[6]
				
					if sys.argv[6].find('.')==-1:
						erflag=5
		else:
			erflag=6

	#checking if the observer is within the area given by the user
	if erflag==0 :
		if x1<startx or x2>endx or y1<starty or y2>endy or startx>endx or endy<starty:
			erflag=2

	vp = [0,0,0]
	if erflag==0:
		with rasterio.open(dsm, 'r+') as r:

			data = r.read()  # read all raster values
		dimensions=data.shape
		if startx<0 or endx>dimensions[2]:
			erflag=4
		

		heights = np.loadtxt(point)
		pointspot=0

		#the following loops represent the coordinates for the observer.If used for one cell then the loops repeat only once
		for y in range(y1, y2):
			for x in range(x1, x2):

				failure=0
				vp[0]=x
				vp[1]=y
			
				for h in range(pointspot,len(heights)):


					if heights[h,5]==vp[0]+1 and heights[h,4]==vp[1]+1:

						vp[2]=data[0][vp[1]][vp[0]]+heights[h,3]
						pointspot=h+1
						failure=1
			
						break
					if heights[h,4]>vp[1]+1:
						break
				#if the observers height isnt found in the file then the cell is skipped
				if failure==0:

					vp[2]=data[0][vp[1]][vp[0]]

			
				if rank==0:

					print("calculating viewshed for (x,y): (",vp[0],",",vp[1],")")

				viewshed(vp,data,startx,endx,starty,endy,dsm)
	elif erflag==1:
		print("Invalid coordinates for observer. Try using an integer")
	elif erflag==2:
		print("Invalid coordinates for observer. Observer placed out of DEM")
	elif erflag==3:
		print("Invalid coordinates for DEM location. Try using again like this: 2-10 ") 
	elif erflag==4:
		print("Invalid coordinates. The given coordinates are out of bounds")
	elif erflag==5:
		print("Invalid file name for the forth argument")
	elif erflag==6:
		print("invalid third argument.Input either a DEM file or custom limits for DEM")
	elif erflag==7:
		print("Invalid input given. Input coordinates for observer")
	elif erflag==8:
		print("Invalid argument. Limits only given for x")

def	viewshed(vp,data,startx,endx,starty,endy,dsm):
	#print("-------------------------------")
	start_time = time.time()

	if rank!=0 or size==1:

		newData = [[0 for y in range(endy)] for x in range(endx)]  
		#the lists below are used in the visibility function to keep the pixel events values
		#max keeps the max height for every pixel at any point
		maxheight=[]



		#currentdist have the distance from the observer for the enter-center and EXIT events
		currentdist1 = []

		#angle has the angle for the enter,center and EXIT event
		angle0 =[]
		angle1 =[]
		angle2 =[]

		#height has the height of enter and EXIT events
		height0= []
		height1= []
		height2 =[]
	




	

		#vp[2] is the height at the pixel of the observer
		#vp[1] is the y coordinate for the pixel of the observer
		#vp[0] is the x coordinate for the pixel of the observer


		#if the algorith uses one or two processes then the algorith is linear-the calculation occurs in a single process
		if size!=1:
			#split calculates and returns the angles of the part that every process calculates
			sizeoftif= (endy-1-starty)*(endx-1-startx)
			sections=[None] *(size)
			sections=split(sizeoftif,vp,startx,endx,starty,endy)
			slicestart=sections[rank-1]
			sliceend=sections[rank]

		else:

			#if one process is used, it calculates all the cells 
			slicestart=0
			sliceend=2*math.pi

		#the rotation function calculates the events of the cells for every process
		lst,currentdist1,angle0,angle1,angle2,height0,height1,height2,maxheight,i=par2.rotation(slicestart,sliceend,vp,data,startx,endx,starty,endy)

		#function visibility calculates the visibility of every cell using as input the calculations from  the rotation function
		if size==1:
			#if only one process is used, the output is returned in the newdata array
			newData=par3.visibility(lst,vp,slicestart,sliceend,currentdist1,angle0,angle1,angle2,height0,height1,height2,maxheight,i,startx,endx,starty,endy)

		else:
			#visibilitys output is returned by ireceiv 
			par3.visibility(lst,vp,slicestart,sliceend,currentdist1,angle0,angle1,angle2,height0,height1,height2,maxheight,i,startx,endx,starty,endy)
		#elapsed_time = time.time() - start_time
		#print("time psed for checking visibility",elapsed_time,"for rank",rank)

	


	if rank==0 :

		if size!=1:
			for k in range(1,size):
				#if more than 1 process is used, the visiblity output is collected by the rank=0 process
				req=comm.irecv(100000000,source=k,tag=k)
				newData=req.wait()

				for i in range(0,len(newData)):
						outsingle[0][newData[i][1]][newData[i][0]]=newData[i][2]
				outputarray[0][vp[1]][vp[0]]+=len(newData)
		else:
			for i in range(0,len(newData)):
				outsingle[0][newData[i][1]][newData[i][0]]=newData[i][2]
			outputarray[0][vp[1]][vp[0]]+=len(newData)
		elapsed_time = time.time() - start_time
		print("visibility calculation completed for rank 0 in(sec):",elapsed_time)

	#try: 
	#	img.show()
	#except: 
	#	pass


		with rasterio.open(dsm, 'r+') as src:		
			ras_meta = src.profile
		


   	 # Add GeoTIFF-specific keyword arguments.
		ras_meta['dtype'] = 'int32'#'uint16'
		ras_meta['tiled'] = False
		ras_meta['compress'] = 'lzw'
		ras_meta['nodata'] = 0
		
   	#	ras_meta['blockxsize'] = 320
  		#ras_meta['blockysize'] = 240
		cordx=str(vp[0])
		cordy=str(vp[1])
		name="viewshed for x "+cordx+"and y"+cordy
		with rasterio.open(name+'.tif', 'w', **ras_meta) as dst:
			dst.write(outsingle)
		with rasterio.open('output.tif', 'w', **ras_meta) as dst:
			dst.write(outputarray)
		if outputflag==1:
			statistics(vp,startx,endx,starty,endy,outsingle)

def	statistics(vp,startx,endx,starty,endy,outsingle):
	correct=0
	correct1=0
	correct2=0				
	wrongvis=0
	wronginvis=0
	print("statistics mode")

	with rasterio.open(comparestring, 'r+') as a:
			grass = a.read()  # read all raster values
	for i in range(startx+1,endx-1):
		for j in range(starty+1,endy-1):


			if  (grass[0][j][i]==1 and outsingle[0][j][i]==1 )  :
				correct1+=1
			elif (grass[0][j][i]==1 and outsingle[0][j][i]!=1 )  :
				wronginvis+=1
			elif (grass[0][j][i]!=1 and outsingle[0][j][i]==1 )  :
				wrongvis+=1
			else:
				correct2+=1

	
	producersvis=correct1/(correct1+wrongvis)
	usersvis=correct1/(correct1+wronginvis)
	producersinvis=correct2/(correct2+wronginvis)
	usersinvis=correct2/(correct2+wrongvis)
	expectedagreement=((correct1+wronginvis)*(correct1+wrongvis)+(correct2+wronginvis)*(correct2+wrongvis))/(correct1+correct2+wrongvis+wronginvis)
	observedagreement=correct1+correct2
	kcoefficient=(observedagreement-expectedagreement)/((correct1+correct2+wrongvis+wronginvis)-expectedagreement)

	print("producers accuracy for visible cells :", producersvis)
	print("producers accuracy for invisible cells :", producersinvis)
	print("users accuracy for visible cells :", usersvis)
	print("users accuracy for invisible cells :", usersinvis)
	print("kcoefficient", kcoefficient)	
	print("kcoefficient :", kcoefficient)	

#Split is used to divide the workload of every process equally
def	split(sizeoftif,vp,startx,endx,starty,endy):

		#calculating the area size and dividing by the number of processes
		sidex=endx-1-startx
		sidey=endy-1-starty
		share=sizeoftif/(size-1)
		sections=[None] *(size)
		sections[0]=0
		initx=endx-1
		inity=vp[1]
		height=initx-vp[0]
		leftoverside=(endy-1-inity)
		sameside=leftoverside
		
		#every pace of the for loop calculates the angle for one process
		for i in range(1,size):

			leftovershare=share-leftoverside*height/2
			#every pace of the calculates the area of the triangle between the observer and a side of the DSM
			#if the triangle is less that the area needed for the process then the calculation is repeated for the next side of the dem for the remaining area
			while leftovershare>0:

				sameside=0

				if initx==endx-1 :
					inity=endy-1
					initx=-1
					height=endy-1-vp[1]
					leftoverside=sidex
				elif initx==startx:
					inity=starty
					initx=-1
					height=vp[1]-starty
					leftoverside=sidex
				elif inity==endy-1 :
					initx=startx  
					inity=-1
					height=vp[0]-startx
					leftoverside=sidey					
				elif inity==starty:
					inity=-1
					initx=endx-1
					leftoverside=sidey
					height=endx-1-vp[0]

				leftovershare -=leftoverside*height/2

			leftovershare +=leftoverside*height/2
			if initx==endx-1 or initx==startx:

				if  initx==startx:

					if sameside!=0:
						sameside=(sidey-sameside)
					inity=endy-1-(2*leftovershare/(height))	-sameside	
					leftoverside=inity-starty

				else:
					if sameside!=0:
						sameside=(sidey-sameside)

					inity=starty+(2*leftovershare/(height))+sameside
					leftoverside=endy-1-inity
			else:

				if  inity==starty:
					if sameside!=0:
						sameside=(sidex-sameside)
					initx=startx+(2*leftovershare/(height))+sameside
					leftoverside=endx-1-initx

				else:
					if sameside!=0:
						sameside=(sidex-sameside)
					initx=endx-1-(2*leftovershare/(height))-sameside
					leftoverside=initx-startx
			sameside=leftoverside
			angle=math.atan2((inity-vp[1]),(initx-vp[0]))

			sections[i]=angle
			if sections[i]<=0:
				sections[i]=(2*math.pi+angle)
		sections[size-1]=(math.pi*2)
		return 		sections
	
main()
