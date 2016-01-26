wx_list = ['wx', 'boy', 'eighteen?'] #define a list

print(wx_list)	#print the list

print(len(wx_list))	#print the size of list

for x in xrange(0, len(wx_list)):
	print(wx_list[x])
	pass

#print(wx_list[4])  #there will be a error

print(wx_list[-1])  #to access the end of the list


wx_list.append('yes') #append to the end
print(wx_list[-1])

wx_list.insert(1, 'man') #insert to  where index = 1
print(wx_list)

print(wx_list.pop(1)) #to ...pop a value, and we can print it 
print(wx_list)

wx_list[1] = 'girl' #to change a value, so easy
print(wx_list) 

#------------------------------------------------------------------#

list1 = ['str', 1, 2.3, True] #the value in list can be more than 1 type
print(list1)

list2 = ['str', ['str1', 'str2'], 'str3'] #list can be a value of a list
print(list2) 
print(len(list2)) #3















