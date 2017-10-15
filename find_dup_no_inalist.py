# Write code to filter duplicate elements from an array and print as a list?
def unique(inlist):
    opdict = {}

    for num in inlist:
        # add the number is it is not a key
        if not num in opdict.keys(): 
            opdict[num] = 1 
        else:
            print("This num {} is a dup = {}".format(num, opdict))
    return opdict.keys()

inlist = [12, 4, 6, 12, -4, +4, 4, 90, 33, 4]

print("\n")
print unique(inlist)




