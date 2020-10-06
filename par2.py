#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import numpy




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
#viewpoint location

#temporary limits to image size for  x->startx<x<endx
#this will be removed for the finel version of the code
#and the image size will be the full image
#the function pixel event calculates the height,angle and distance for every pixel 
#and every type of event(center ,EXIT,enter) and saves them in the lst list


#the function rotation emulates a half line that rotates counter clock wise 
#around the observerver and for every pixel it passes through it calculates
#some values for every pixel's enter ,EXIT and center event and returns the lst with
#these values for every pixel.		
def rotation(anglestart,angleend,vp,data,startx,endx,starty,endy):

	#lst is the list that will contain all the events for the pixels the half line meets

	if angleend>math.pi and anglestart<math.pi:
		

		xstart,xend,currentpace,flag=gridx(anglestart,math.pi,vp,startx,endx,starty,endy)
		coordinates=gridy(xstart,xend,anglestart,math.pi,currentpace,flag,anglestart,vp,startx,endx,starty,endy)
		xstart,xend,currentpace,flag=gridx(math.pi,angleend,vp,startx,endx,starty,endy)
		l2=gridy(xstart,xend,math.pi,angleend,currentpace,flag,anglestart,vp,startx,endx,starty,endy)
		for c in range(0,len(l2)):
				coordinates.append([])
				coordinates[len(coordinates)-1].append(l2[c][0])
				coordinates[len(coordinates)-1].append(l2[c][1])

	
		
	else:
		xstart,xend,currentpace,flag=gridx(anglestart,angleend,vp,startx,endx,starty,endy)
		coordinates=gridy(xstart,xend,anglestart,angleend,currentpace,flag,anglestart,vp,startx,endx,starty,endy)
	
	lst=pixelcalc(coordinates,data,anglestart,angleend,vp)

	lst=sorted(lst, key=lambda x: x[0])
	i=0
	while(len(lst)>i  ):

		if lst[i][0]>=anglestart :
			break
		i+=1

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

	initlist(i,lst,data,vp,currentdist1,angle0,angle1,angle2,height0,height1,height2,maxheight,startx,endx,starty,endy)
	
	return lst,currentdist1,angle0,angle1,angle2,height0,height1,height2,maxheight,i

#grid x calculates the limits in the x axis for each process
def gridx(anglestart,angleend,vp,startx,endx,starty,endy):


	flag=0
	#calculation for 1-2 quadrant
	if anglestart<math.pi:
		if anglestart==0:
			limx1=endx-1
		else:
			limx1=int((endy-1-vp[1])/math.tan(anglestart)+vp[0])
		limx2=int((endy-1-vp[1])/math.tan(angleend)+vp[0])

		if limx1>vp[0]:
			limx1+=1
		if limx2>vp[0]:
			limx2+=1	
		#limits cant exceed the boarder of the DSM
		if limx2<startx:
			limx2=startx
		if limx1>=endx:
			limx1=endx-1	
		if limx1<startx:
			limx1=startx
		if limx2>=endx:
			limx2=endx-1

		#checks if the area resided in one quadrant and gives it a flag.
		# flag=1-> process in only 1 quadrant
		# flag=0-> process in more than 1 quadrant
		if (angleend<math.pi/2): 
			flag=1
			limx2=vp[0]-1
		elif (anglestart>math.pi/2)  :
			flag=1
			limx1=vp[0]
		x=limx1
		currentpace=-1

		return x,limx2,currentpace,flag
	#calculation for 3-4 quadrant
	else:


		limx1=int((starty-vp[1])/math.tan(anglestart)+vp[0])
		limx2=int((starty-vp[1])/math.tan(angleend)+vp[0])
		if limx1>vp[0]:
			limx1+=1
		if limx2>vp[0]:
			limx2+=1	

		#limits cant exceed the boarder of the DSM
		if limx2<startx:
			limx2=startx
		elif limx2>=endx:
			limx2=endx-1

		if limx1<startx or anglestart==math.pi:
			limx1=startx
		elif limx1>=endx:
			limx1=endx-1	

		#checks if the area resided in one quadrant and gives it a flag.
		# flag=1-> process in only 1 quadrant
		# flag=0-> process in more than 1 quadrant
		if (angleend<3*math.pi/2)   :

			limx2=vp[0]		
			flag=1


		elif (anglestart>3*math.pi/2):
			flag=1
			limx1=vp[0]


		x=limx1
		currentpace=1

		return x,limx2,currentpace,flag
#	grid x calculates the limits in the y axis for each process
def gridy(xstart,xend,anglestart,angleend,currentpace,flag,fs,vp,startx,endx,starty,endy):

	coordinates=[]
	for x in range(xstart,xend,currentpace):
		# flag=0-> process in more than 1 quadrant
		if flag==0:
			if currentpace<0 :
				limity1=int(math.tan(anglestart)*((x)-vp[0]-1)+vp[1])
				limity2=int(math.tan(angleend)*((x)-vp[0]+1)+vp[1])		
				y=endy-1
			else:
				limity1=int(math.tan(anglestart)*((x+1)-vp[0])+vp[1])+1
				limity2=int(math.tan(angleend)*((x-1)-vp[0])+vp[1])+1
				y=starty
		# flag=1-> process in only 1 quadrant and the calculatin depends on the quadrant
		else:
			limity1=int(math.tan(anglestart)*((x)-vp[0])+vp[1])
			limity2=int(math.tan(angleend)*((x)-vp[0])+vp[1])

			
			#seting the limmits of the calculation to the limits of DSM
			if limity1>endy-1:
				limity1=endy-1
			elif limity1<starty:
				limity1=starty
			if limity2>endy-1:
				limity2=endy-1
			elif limity2<starty:
				limity2=starty	
			#calculating between the anglestart and angleend of each process
			if currentpace<0  and angleend<=math.pi/2 :
				limity1=int(math.tan(anglestart)*((x)-vp[0]-1)+vp[1])-1
				y=int(math.tan(angleend)*((x)-vp[0]+1)+vp[1])+1

			elif currentpace<0 and anglestart>=math.pi/2 :

				y=int(math.tan(anglestart)*((x)-vp[0]-1)+vp[1])+1

			if currentpace>0 and   anglestart>=3*math.pi/2 :

				y=int(math.tan(anglestart)*((x)-vp[0]+1)+vp[1])-1

			elif currentpace>0 and  angleend<=3*math.pi/2 :	

				y=int(math.tan(angleend)*((x)-vp[0]-1)+vp[1])-1

				limity1=int(math.tan(anglestart)*((x)-vp[0]+1)+vp[1])+1

		if y>endy-1:
			y=endy-1
		elif y<starty:
			y=starty
		#if one process starts before angle=math.pi then the calculation for math.pi is divided manualy to the processes
		#in order to avoid a duplicate calculation that would create errors
		if currentpace>0 :
			if (anglestart==math.pi and fs<math.pi and x<vp[0]or(fs==0 and angleend==math.pi*2)) :
				if y>=vp[1]:
					y=vp[1]-1
				if limity1>=vp[1]:
					limity1=vp[1]-1
				if limity2>=vp[1]:
					limity2=vp[1]-1
			else:
				if y>=vp[1]:
					y=vp[1]
				if limity1>=vp[1]:
					limity1=vp[1]
				if limity2>=vp[1]:
					limity2=vp[1]

		else:
			if y<vp[1]:
				y=vp[1]
			if limity1<vp[1]:
				limity1=vp[1]
			if limity2<vp[1]:
				limity2=vp[1]
		#x and y coordinates are saved in the coordinates list
		while ((( (y>=limity1 and  x>=vp[0])or(y>=limity2 and  x<=vp[0]))and currentpace<0)  or ( ((y<=limity2 and  x>=vp[0])or(y<=limity1 and  x<=vp[0]))and currentpace>0) ) :

				coordinates.append([])

				coordinates[len(coordinates)-1].append(x)
				coordinates[len(coordinates)-1].append(y)

				y+=currentpace
	return coordinates
#Pixelcalc claculates the quadrant a cell resides in.Depending on the quadrant the cell is 
#assigned by spesific pointers which are needed in oder to calculate the events for the cell.
#After assigning the pointers to the cell, the events of every call are calculated
def pixelcalc(coordinates,data,anglestart,angleend,vp):

		lst=[]
		for i in range(0,len(coordinates)):
				x=coordinates[i][0]
				y=coordinates[i][1]
				if y==vp[1] and  x>vp[0] :
			
					x0=-1
					y0=-1
					x2=-1
					y2=1

				elif x>vp[0] and y>vp[1]:
					x0=1
					y0=-1
					x2=-1
					y2=1

				#for events with angle=90
				elif x==vp[0] and y>vp[1]:
					x0=1
					y0=-1
					x2=-1
					y2=-1

				#for events with 90<angle<180
				elif x<vp[0] and y>vp[1]:
					x0=1
					y0=1
					x2=-1
					y2=-1
				#for events with angle=180
				elif x<vp[0] and y==vp[1]:
					x0=1
					y0=1
					x2=1
					y2=-1
				#for events with 180<angle<270
				elif x<vp[0] and y<vp[1]:
					x0=-1
					y0=1
					x2=1
					y2=-1
				#for events with angle=270
				elif x==vp[0] and y<vp[1]:
					x0=-1
					y0=1
					x2=1
					y2=1
				#for events with 270<angle<360
				elif x>vp[0] and y<vp[1]:
					x0=-1
					y0=-1
					x2=1
					y2=1
				else:
					continue

				angle0=math.atan2((y+(0.5*y0)-vp[1]),(x+(0.5*x0)-vp[0]))
				#because atan2 returns nurmbers between π and -π when we find negative angles we add 2*π
				if angle0<0 :
					angle0+=2*math.pi

				#angle for center event
				angle1=math.atan2((y-vp[1]),(x-vp[0]))
				#because atan2 returns nur	mbers between π and -π when we find negative angles we add 2*π
				if angle1<0:
					angle1+=2*math.pi

				#angle for EXIT event
				angle2=math.atan2((y+(0.5*y2)-vp[1]),(x+(0.5*x2)-vp[0]))
				#because atan2 returns nurmbers between π and -π when we find negative angles we add 2*π
				if angle2<0:
					angle2+=2*math.pi
			
				x01=x
				x02=x+1*x0
				y01=y
				y02=y+1*y0
				q1=data[0][y01][x01]
				q2=data[0][y01][x02]
				q3=data[0][y02][x01]
				q4=data[0][y02][x02]
				height0=((q1+q2+q3+q4)/4)
				h0=height0
				#EXIT event height with interpolation
				#form the average of the 4 neighbouring pixels
				x01=x
				x02=x+1*x2
				y01=y
				y02=y+1*y2
				q1=data[0][y01][x01]
				q2=data[0][y01][x02]
				q3=data[0][y02][x01]
				q4=data[0][y02][x02]
				height2=((q1+q2+q3+q4)/4)
				h2=height2
				#distance from observer for enter event
				distx=(x+(0.5*x0)-vp[0])*3
				disty=(y+(0.5*y0)-vp[1])*3
				distance0=math.sqrt(((disty)**2)+((distx**2)))

				#distance from observer for enter event
				distx=(x-vp[0])*3
				disty=(y-vp[1])*3
				distance1=math.sqrt(((disty)**2)+((distx**2)))

				#distance from observer for EXIT event
				distx=(x+(0.5*x2)-vp[0])*3
				disty=(y+(0.5*y2)-vp[1])*3
				distance2=math.sqrt(((disty)**2)+((distx**2)))

				height1=data[0][y][x]
				h1=height1
				adj=distance1**2/(2*6370997)
				height1-=adj
				height1=math.atan2((height1-vp[2]),(distance1))


				adj=distance2**2/(2*6370997)
				height2-=adj
				height2=math.atan2((height2-vp[2]),(distance2))

				adj=distance0**2/(2*6370997)
				height0-=adj
				height0=math.atan2((height0-vp[2]),(distance0))

				if  anglestart<=angle2 or angle2<=angleend:
					lst.append([])
					lst[len(lst)-1].append(angle2)
					lst[len(lst)-1].append("EXIT")
					lst[len(lst)-1].append(distance1)

				if  anglestart<=angle1 or angle1<=angleend:
					lst.append([])
					lst[len(lst)-1].append(angle1)
					lst[len(lst)-1].append("CENTER")
					lst[len(lst)-1].append(distance1)			

				if anglestart<=angle0 or angle0<=angleend:
					if	y==vp[1] and x>vp[0] and (anglestart<=math.pi/4 and anglestart!=0):
						angle0-=2*math.pi
					elif	y==vp[1] and x>vp[0] :
						angle2+=2*math.pi
						angle1+=2*math.pi		

					#put the calculated values in the list
					lst.append([])
					lst[len(lst)-1].append(angle0)
					lst[len(lst)-1].append("ENTER")
					lst[len(lst)-1].append(distance1)
					lst[len(lst)-1].append(angle1)
					lst[len(lst)-1].append(angle2)
					lst[len(lst)-1].append(height0)
					lst[len(lst)-1].append(height1)
					lst[len(lst)-1].append(height2)


		return lst


#initlist is a function that initializes the lists(:currentdist0,currentdist1,currentdist2,currentx,currenty,angle0,
#  angle1,angle2,height0,height2,maxheight)before we start the prossess of taking 
#the events out of the lst. The initlist inputs the pixels that the line currently intersects as enter events.
#If we dont initialize the list it will bug out when we start the visiblity function.
#the output of this function is the output of entervent function which this function uses,
#as input we use the spot in the lst which contains the angle we need to initialize for and the lst with the pixel events.

#**this function isnt complete.For now it initializes the list for angle=0  and for 90>degrees>45  	

def initlist(i,lst,data,vp,currentdist1,angle0,angle1,angle2,height0,height1,height2,maxheight,startx,endx,starty,endy):

	#firstly it checks the angle to determine the equation of the straight line we ll use
	#if (the targent of the angle)>1 or (the targent of the angle)<-1 we ll use x=λ*y , λ is the targent of the angle
	#if (the targent of the angle)<1 or (the targent of the angle)>-1 we ll use y=λ*x , λ is the targent of the angle
	#i explain this further in the read me file
	
	
	#the if needs to be reworked.It should determine from the angle the
	#type of equitation and and depending on the quadrant setup the for loop properly
	#for both positive targents and negative targents with the apropriate pace(: x++ or x--)
	startinit=vp[1]

	if lst[i][0]>math.pi:
		endyinit=starty	
		pacex0=-1
		pacex2=1
		pacey0=-1
		pacey2=1
		if lst[i][0] <3*math.pi/2:
			pacey0=1
			pacey2=-1
		if lst[i][0] ==3*math.pi/2:
			pacey0=1
	elif lst[i][0]<math.pi and lst[i][0]!=0:
		endyinit=endy-1	
		pacex0=1
		pacex2=-1
		pacey0=1
		pacey2=-1
		if lst[i][0] <math.pi/2:
			pacey0=-1
			pacey2=1

		if lst[i][0] ==math.pi/2:
			pacey0=-1
	else:
		endyinit=vp[1]
		if lst[i][0]==0:
			pacex0=-1
			pacex2=-1
			pacey0=-1
			pacey2=1
		elif lst[i][0]==math.pi:
			pacex0=1
			pacex2=1
			pacey0=1
			pacey2=-1

#-----------------------------------------------------------------------------------------

	if lst[i][0] <2*math.pi and lst[i][0] >math.pi :
		paceyinit=-1

	else:
		paceyinit=1
	x1=vp[0]
	if   lst[i][0]<3*math.pi/2 and lst[i][0]>math.pi/2 :
		pacexinit=-1
	else:
		pacexinit=1 
	for y in range(vp[1],endyinit+paceyinit,paceyinit):

		if lst[i][0]==0:
			x2=endx
		elif lst[i][0]==math.pi:
			x2=startx
		else:
			x2=((y+0.5*pacex0-vp[1])/math.tan(lst[i][0]))+vp[0]

		x=int(x2)

		if(x2-x>0.5000001 ): 
			x2=x+1
		elif(x2-x<0.4999999):
			x2=x
		else:
			if(  lst[i][0]<math.pi  ):
				x2=x+1

			else:
				x2=x
		

		for x in range(x1,x2+pacexinit,pacexinit):

			if x<=endx-1 and x>=startx and y<=endy-1 and y>=starty:

				enterevent(	x,y,pacex0,pacey0,pacex2,pacey2,data,lst,i,vp,currentdist1,angle0,angle1,angle2,height0,height1,height2,maxheight)
	
		if  x2>endx-1 or x2<startx:

			break
		x1=x2
		
		
#the function entervent works in the same way as pixelevent but it only calculates and
#inputs the enter event for every pixel in the lst

#the input for the function is the same as the function pixelevent:the x,y coordinates of the pixel
#we examine and pacex0,pacey0,pacex2,pacey2 which are either -1 or +1		
#this function returns lst with the new eneter events in it
def enterevent(	x,y,pacex0,pacey0,pacex2,pacey2,data,lst,i,vp,currentdist1,angle0,angle1,angle2,height0,height1,height2,maxheight):

		if y==vp[1] and x!=vp[0]:
			if x>vp[0]:
				pacex0=-1
				pacey0=-1
				pacex2=-1
				pacey2=1
			else:
				pacex0=1
				pacey0=1
				pacex2=1
				pacey2=-1
		if x==vp[0] and y!=vp[1]:
			if y>vp[1]:
				pacex0=1
				pacey0=-1
				pacex2=-1
				pacey2=-1
			else:
				pacex0=-1
				pacey0=1
				pacex2=1
				pacey2=1
		
		if x==vp[0] and y==vp[1] :
			return
	
		#enter event height with interpolation	
		x01=x
		x02=x+1*pacex0
		y01=y
		y02=y+1*pacey0
		q1=data[0][y01][x01]
		q2=data[0][y01][x02]
		q3=data[0][y02][x01]
		q4=data[0][y02][x02]

		height00=((q1+q2+q3+q4)/4)

		#EXIT event height with interpolation
		x01=x
		x02=x+1*pacex2
		y01=y
		y02=y+1*pacey2
		q1=data[0][y01][x01]
		q2=data[0][y01][x02]
		q3=data[0][y02][x01]
		q4=data[0][y02][x02]
		height02=((q1+q2+q3+q4)/4)

		#distance from observer for enter event
		distx=(x+(0.5*pacex0)-vp[0])*3
		disty=(y+(0.5*pacey0)-vp[1])*3
		distance0=math.sqrt(((disty)**2)+((distx**2)))

		#distance from observer for enter event
		distx=(x-vp[0])*3
		disty=(y-vp[1])*3
		distance1=math.sqrt(((disty)**2)+((distx**2)))


		#distance from observer for EXIT event
		distx=(x+(0.5*pacex2)-vp[0])*3
		disty=(y+(0.5*pacey2)-vp[1])*3
		distance2=math.sqrt(((disty)**2)+((distx**2)))

		#angle for enter event
		angle00=math.atan2((y+(0.5*pacey0)-vp[1]),(x+(0.5*pacex0)-vp[0]))


		#angle for center event
		angle01=math.atan2((y-vp[1]),(x-vp[0]))
		
		#because atan2 returns nurmbers between π and -π when we find negative angles we add 2*π
		if angle00<0 and( angle01!=0 ):
			angle00+=2*math.pi		
		
		#because atan2 returns nurmbers between π and -π when we find negative angles we add 2*π
		if angle01<0  :
			angle01+=2*math.pi
	
		#angle for EXIT event
		angle02=math.atan2((y+(0.5*pacey2)-vp[1]),(x+(0.5*pacex2)-vp[0]))
		#because atan2 returns nurmbers between π and -π when we find negative angles we add 2*π
		if angle02<0:
			angle02+=2*math.pi
	
		
		if  y==vp[1] and x>vp[0] and lst[i][0]>math.pi/4 :#2*math.pi-math.pi/4:
			angle00+=2*math.pi
			angle01+=2*math.pi
			angle02+=2*math.pi

		#put the calculated values in the list
		angle0.append(angle00)
		angle1.append(angle01)
		angle2.append(angle02)
		currentdist1.append(distance1)

		
		height01=data[0][y01][x01]
		adj=distance1**2/(2*6370997)
		height01-=adj
		height01=math.atan2((height01-vp[2]),(distance1))


		adj=distance2**2/(2*6370997)
		height02-=adj
		height02=math.atan2((height02-vp[2]),(distance2))

		adj=distance0**2/(2*6370997)
		height00-=adj
		height00=math.atan2((height00-vp[2]),(distance0))
		height0.append(height00)
		height1.append(height01)
		height2.append(height02)
		curemax=max(height00,height01,height02)
		maxheight.append(curemax)

		
