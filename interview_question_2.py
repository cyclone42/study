# Find the 2 largest numbers in an array.

def largest_array(input_list):
    print("here is the input = {}".format(input_list))
    # keep the two largest number in this list
    largest_no = [] 
    
    length = len(input_list)

    if length > 2:
        # run the loop
        result = sort_list(input_list, length)  # It will return list of 2 largest numbers [10, 15] 
        print("\n")
        print("Here is the answer = {}".format(result)) 
    elif length == 2:
        return input_list.sort()
    else:
        return None


def sort_list(input_list, length):

    largest_no = []
    if input_list[0] > input_list[1]:
        largest_no =[input_list[1], input_list[0]]    
    else:
        largest_no =[input_list[0], input_list[1]]
    print("Before start = {}".format(largest_no))
   
    for i in range(2, len(input_list)):
        print("item = {}".format(input_list[i]))
        if largest_no[1] < input_list[i] > largest_no[0]:
            largest_no[0] = largest_no[1]
            largest_no[1] = input_list[i]
            print("first loop start = {}".format(largest_no))
        elif largest_no[1] > input_list[i] > largest_no[0]:
            largest_no[0] = input_list[i]
            print("second loop start = {}".format(largest_no))
        else:
            print("Number is less than both largest nos")
    return largest_no    



input_list = [12, 14, 90, 22, -6, -1000, 500]
largest_array(input_list)


# Second method
sorted_list = sorted(input_list)
#print("Here are - 2 largest numbers {}, {}".format(sorted_list[-2:]))


# Third  method - inplace sorting
input_list.sort()
#print("Here are 2 largest numbers {}, {}".format(input_list[-2:]))





