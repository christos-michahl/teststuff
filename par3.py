#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
from mpi4py import MPI
import time
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


def bisearch(dist,target):

	current=len(dist)//2
	edge1=1
	edge2=len(dist)

	while dist[current-1]!=target :

		if dist[current-1]<target:

			if edge1!=current+1:
				edge1=current+1
				current+=(edge2-edge1)//2
			else:
				current+=1
		elif dist[current-1]>target:

			if edge2!=current-1:
				edge2=current-1
				current-=(edge2-edge1)//2
			else:
				current-=1


	while dist[current-2]==dist[current-1]:
		current-=1


	return current-1

#used binary search to find best possible spot for an elemnt that 
#doesnt exist in the list.As input it has dist which is the array we look in and 
#target which is element for which we are searching the optimal spot.
#As output it returns the spot we should insert our target
def maxbisearch(dist,target):

	current=len(dist)//2
	edge1=0
	edge2=len(dist)-1

	while edge1<=edge2:

		current=(edge1+edge2)//2
		if dist[current]<=target:

			edge1=current+1
		elif dist[current]>target:

			edge2=current-1

	return edge1

	

		
#the visiblity function reads the list and processes every event depending on its type.
#As input it needs: the lst with the events,the data list which contains the heights of every pixel
#the datacomp which is the data from the grass in order to determine the accuracy
#and vp which contains the x,y and height of the viewpoint.
#Currently the is no output for visibility. In future versions it will probaly keep the visible pixels in an array .
def visibility(lst,vp,slicestart,sliceend,currentdist1,angle0,angle1,angle2,height0,height1,height2,maxheight,i,startx,endx,starty,endy):
	output=[]

	start_time = time.time()
	#counter for output list
	place=0
	place0=0
	place1=0
	place2=0

		
	#---------------------------------------------------------START-------------------------------------------------------------
	#pull events one by one from the list
	for count1 in range(i,len(lst)):	
		if lst[count1][0]<slicestart:
			continue
		if lst[count1][0]>=sliceend :#and rank!=size-1:
			break
	
		#in the enter event we input the new pixel in the list based on distance from the viewpoint
		if lst[count1][1]=="ENTER" :

			failsafe=len(currentdist1)
			#before binary search we check if the new event is the min or the max of the list
			#and has to go first or last in the list

			if len(currentdist1)==0:
				continue

			#this i checks if its bigger than the last spot on the list
			if currentdist1[len(currentdist1)-1]<lst[count1][2]:
				i=len(currentdist1)

			#this  checks if its less than the first spot on the list
			elif  currentdist1[0]>lst[count1][2]:
				i=0

			#binary search to find the spot the pixels fits in based on distance
			else:

				i=maxbisearch(currentdist1,lst[count1][2])

			angle0.insert(i,lst[count1][0])
			currentdist1.insert(i,lst[count1][2])
			angle1.insert(i,lst[count1][3])
			angle2.insert(i,lst[count1][4])
			height0.insert(i,lst[count1][5])
			height1.insert(i,lst[count1][6])
			height2.insert(i,lst[count1][7])

			#calculate max possible height for pixel
			curemax=max(height0[i],height1[i])
			maxheight.insert(i,curemax)


		#in EXIT events we delete from the list the pixel
		elif lst[count1][1]=="EXIT" :

			i=bisearch(currentdist1,lst[count1][2])
			'''
			try:
				i=currentdist1.index(lst[count1][2])
			except:
				continue
			'''
			del currentdist1[i]
			del angle0[i]
			del angle1[i]
			del angle2[i]
			del height0[i]
			del height1[i]
			del height2[i]
			del maxheight[i]





		#in the center event we check for visibility
		elif lst[count1][1]=="CENTER":


			#-1000 is an imposible value we give max vis in order to initialize it
			#maxvis the biggest height on the list
			maxvis=-10000
			#we find the position of the event with the center event on the list 
			#in order not to make further calculations after we reach the event

			countvis=bisearch(currentdist1,lst[count1][2])
			'''
			try:
				countvis=currentdist1.index(lst[count1][2])
			except:
				continue
			'''

			
			for i in range(0,countvis,1):
	

##################################################################################################################

				#for the pixels with distance less than the current pixel we calculate their height
				#based on their enter ,center and EXIT angle and their enter EXIT and cnter height using interpolation

				if  maxheight[i]>=height1[countvis] :#and minheight[i]<height : #	if totalmax==maxheight[i] and maxheight[i]>h1:
					place+=1

					if(lst[count1][0]<angle1[i]):

							place0+=1

							#we calculate the height of the pixel in the list based on its enter ,center and EXIT angle and their
							#enter EXIT and cnter height using interpolation
							curheight=height1[i]+(height0[i]-height1[i])*(angle1[i]-lst[count1][0])/(angle1[i]-angle0[i])

					elif(lst[count1][0]>angle1[i]):

							place2+=1
							#we calculate the height of the pixel in the list based on its enter ,center and EXIT angle and their
							#enter EXIT and cnter height using interpolation
							curheight=height1[i]+(height2[i]-height1[i])*(lst[count1][0]-angle1[i])/(angle2[i]-angle1[i])

					else:

						place1+=1
						curheight=height1[i]

					if maxvis<curheight:
						maxvis=curheight

					if maxvis>height1[countvis]:
						break


			if maxvis<=height1[countvis] :


				x=math.cos(angle1[countvis])*currentdist1[countvis]/3+vp[0]
				y=math.sin(angle1[countvis])*currentdist1[countvis]/3+vp[1]
				x1=int(x)
				y1=int(y)

				if x-x1>0.9:
					x=x1+1
				elif x-x1<0.2:
					x=x1

				if y-y1>0.9:
					y=y1+1
				elif y-y1<0.2:
					y=y1
				output.append([])

				output[len(output)-1].append(x)
				output[len(output)-1].append(y)
				output[len(output)-1].append(1)


	if rank!=0:
		#comm.send(output, dest=0,tag=rank)
		req=comm.isend(output, dest=0,tag=rank)
		req.wait()
	return output