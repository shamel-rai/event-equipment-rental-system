from datetime import datetime


def getItemByItemNumber(itemNumber):
    with open('equipment-list.txt') as file:
        lines = file.readlines()

    itemCount = 0
    for line in lines:
        itemCount += 1
        if (itemCount == itemNumber):
            return True, line

    return False, None


def modifyEquipmentQuantity(item, quantity, type):
    itemInfoList = item.split(', ')  # comma with a space
    with open("equipment-list.txt", "r") as file:
        equipmentList = file.read()

    if type == "rent":
        newQuantity = int(itemInfoList[3]) - quantity

    elif type == "return":
        newQuantity = int(itemInfoList[3]) + quantity

    newEquipmentInfo = f"{itemInfoList[0]}, {itemInfoList[1]}, {itemInfoList[2]}, {newQuantity}\n"
    equipmentList = equipmentList.replace(item, newEquipmentInfo)

    with open("equipment-list.txt", "w") as file:
        file.write(equipmentList)


def generateInvoice(item, quantity, customerName, type, daysPassed=0):
    currentDateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(":", "_").replace(" ", "_")
    itemInfoList = item.split(', ')  # comma with a space

    if type == "rent":
        # getting the price in float
        value = itemInfoList[2][1:]
        price = float(value)
        grandTotal = quantity * price  # total price customer has to pay

        # filePath = f"rents/rent-invoice-{customerName}-{str(currentDateTime)}.txt"
        filePath = r"rents\rent-invoice-" + customerName + "-" + str(currentDateTime) + ".txt"
        with open(filePath, "w") as file:  # with closes file automatically
            file.write(f"---Rent Invoice---\n")
            file.write(f"Customer Name: {customerName}\n")
            file.write(f"Equipment Name: {itemInfoList[0]}\n")
            file.write(f"Brand: {itemInfoList[1]}\n")
            file.write(f"Date and Time of Rental: {currentDateTime}\n")
            file.write(f"Rate: {itemInfoList[2]}\n")
            file.write(f"Quantity: {quantity}\n")
            file.write(f"Grand Total: ${grandTotal}\n")

    elif type == "return":
        # filePath = f"returns/returns-invoice-{customerName}-{str(currentDateTime)}.txt"
        filePath = r"returns\returns-invoice-" + customerName + "-" + str(currentDateTime) + ".txt"
        with open(filePath, "w") as file:  # with closes file automatically
            file.write(f"---Return Invoice---\n")
            file.write(f"Customer Name: {customerName}\n")
            file.write(f"Equipment Name: {itemInfoList[0]}\n")
            file.write(f"Brand: {itemInfoList[1]}\n")
            file.write(f"Date and Time of Return: {currentDateTime}\n")
            file.write(f"Quantity Returned: {quantity}\n")

            if daysPassed > 5:
                fine = (daysPassed - 5) * 10  # Assuming a fine of $10 per day
                file.write(f"Fine of {daysPassed - 5} days: ${fine}")

    return filePath


def addCustomerFilePath(filePath, customerName):
    with open("customer-file-list.txt", "a") as file:
        file.write(f"{customerName}, {filePath}\n")


def getCustomerFilePathAccordingToItem(customerName, returnQuantity, itemName):
    with open("customer-file-list.txt", "r") as file:
        lines = file.readlines()

    lineNumber = 0
    for line in lines:
        lineNumber += 1
        items = line.split(', ')
        if (items[0] == customerName):  # get correct customer
            with open(f"{items[1][:-1]}", "r") as invoiceFile:
                invoiceLines = invoiceFile.readlines()

            # get correct file (rent invoice of correct item)
            if (invoiceLines[2][16:-1]) == itemName:
                if int(invoiceLines[6][9:-1]) == returnQuantity:
                    # return status with path and lineNumber
                    return True, items[1][:-1], lineNumber
                else:
                    print(
                        f"You have rented {invoiceLines[6][9:-1]} {itemName} from us. Please make sure to return all.")
                    startReturnSystem()

    return False, None, lineNumber


def removeLineFromCustomerFileList(lineNumber):
    file_path = "customer-file-list.txt"

    with open(file_path, "r") as file:
        lines = file.readlines()

    if lineNumber >= 1 and lineNumber <= len(lines):
        # Remove the desired line from the list of lines
        del lines[lineNumber - 1]

    # Write the updated lines back to the file
    with open(file_path, "w") as file:
        file.writelines(lines)


def startRentSystem():
    try:
        itemNumber = int(input("Enter Item Number to Rent: "))

        found, item = getItemByItemNumber(itemNumber)

        if found:
            print("Entered Item Details:")
            displayEquipment(item)
            itemInfoList = item.split(', ')  # comma with a space

            quantity = int(input("Enter Quantity to rent: "))
            if quantity > int(itemInfoList[3]):
                print("Oops! Insufficient Quantity available for rent. Please try again")
                startRentSystem()

            customerName = input("Enter Customer Name: ")

            # modify equipment list file
            modifyEquipmentQuantity(item, quantity, "rent")

            # create invoice
            filePath = generateInvoice(item, quantity, customerName, "rent")
            print(
                f"Successfully created rental invoice!\nStored at: {filePath}")
            addCustomerFilePath(filePath, customerName)
            startSystem()

        else:
            print("Didn't find anything for that Item Number! Please try Again")

    except ValueError:
        print("Invalid input! Please enter a Number.")

    startRentSystem()


def startReturnSystem():
    try:
        itemNumber = int(input("Enter Item Number to Return: "))
        
    except ValueError:
        print("Invalid input! Please enter a Number.1")

    else:
        found, item = getItemByItemNumber(itemNumber)

        if found:
            print("Entered Item Details:")
            displayEquipment(item)
            itemInfoList = item.split(', ')  # comma with a space

            try:
                returnQuantity = int(input("Enter returned Quantity: "))
            except ValueError:
                print("Invalid input! Please enter a Number.2")
            else:
                customerName = input("Enter Customer Name: ")

                found, filePath, lineNumber = getCustomerFilePathAccordingToItem(
                    customerName, returnQuantity, itemInfoList[0])

                if (found):
                    with open(filePath, "r") as file:
                        invoiceLines = file.readlines()

                    rentalDate = datetime.strptime(
                        invoiceLines[4][25:-1], "%Y-%m-%d_%H_%M_%S")
                    daysPassed = (datetime.now() - rentalDate).days

                    if daysPassed > 5:  # exceed 5 days
                        print(f"Customer Returned after exceeding time: {daysPassed} days")
                        invoicePath = generateInvoice(
                            item, returnQuantity, customerName, "return", daysPassed)

                    else:  # within 5 days
                        print("Customer Returned within time")
                        invoicePath = generateInvoice(
                            item, returnQuantity, customerName, "return")

                    print(
                        f"Successfully created return invoice!\nStored at: {invoicePath}")
                    modifyEquipmentQuantity(item, returnQuantity, "return")
                    removeLineFromCustomerFileList(lineNumber)

                else:
                    print("Sorry you haven't rent that product from us!")

                startSystem()

        else:
            print("Didn't find anything for that Item Number! Please try Again")

    startReturnSystem()


def startSystem():
    try:
        print("Enter Your Choice\n1. Rent \n2. Return\n3. Exit")
        adminChoice = int(input("> "))
    
    except ValueError:
        print("Invalid input! Please enter a Number.")
    
    else:
        if adminChoice == 1:
            startRentSystem()
        elif adminChoice == 2:
            startReturnSystem()
        elif adminChoice == 3:
            print("Good Bye!")
            exit()
        else:
            print("Invalid input! Please enter a valid number.")

    startSystem()


def displayEquipment(line):
    splittedLine = line.split(', ') # comma with a space
    print(f"Name: {splittedLine[0]}")
    print(f"Brand: {splittedLine[1]}")
    print(f"Price: {splittedLine[2]}")
    print(f"Quantity Available: {splittedLine[3]}")
    

def getAvailableEquipmentDetails():
    print("Total Equipments available:\n")
    
    with open('equipment-list.txt') as file: # with closes file automatically
        lines = file.readlines()

    itemCount = 0
    for line in lines:
        itemCount += 1
        print(f"Item Number: {itemCount}")
        displayEquipment(line)
        print("--------------------------------------") # to separate different items information
    

def main():
    print("Welcome to Event Equipment Rental System")
    getAvailableEquipmentDetails()
    startSystem()


if __name__ == "__main__": # checks if the current module is being run as the main script
    main()