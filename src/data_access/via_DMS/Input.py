class Input:
    '''
    Handle & validate User input
    '''
    def __init__(self):
        self.job_nums = []
        self.dataset_ids = []
        self.datapackage_id = None

    def other_input(self, InputType, UserInput):
        if InputType ==1:
            self.datapackage_id = int(UserInput)
        if InputType ==2:
            ip = UserInput.split(',')
            for item in [_.strip() for _ in ip]:
                self.dataset_ids.append(int(item))
        if InputType ==3:
            ip = UserInput.split(',')
            for item in [_.strip() for _ in ip]:
                self.job_nums.append(int(item))

    def user_input(self):
        #FIXME : Need to be added execution using data_package_id
        while True:
            print("To run the Meta-protemoics data-analysis workflow \n" \
                  "Three options are available:\n" \
                  "1. enter a datapackage ID\n" \
                  "2. enter a set of dataset-IDs\n" \
                  "3. enter a set of JobNums\n\n" )
            option = int(input("Which option would you like to proceed?\n"))
            if option is 1:
                # 1. Dpkg
                try :
                    ip =   int(input('datapackage ID\n'))
                    self.datapackage_id = ip
                    break
                except Exception as e:
                    print("Incorrect data entered-Not an interger!")
                    print('*' * 10)
            elif option is 2:
                # 2. set of DSs
                try:
                    ip = input('set of dataset ids\n').split(',')
                    for item in [_.strip() for _ in ip]:
                        self.dataset_ids.append(int(item))
                    break
                except Exception as e:
                    print("Incorrect data entered--Not an interger!")
                    print('*'*10)

            elif option is 3:
                # 3. set of JobNums - MSGF+
                try:
                    ip = input("set of Job numbers\n").split(',')
                    for item in [_.strip() for _ in ip]:
                        self.job_nums.append(int(item))
                    break
                except Exception as e:
                    print("Incorrect data entered--Not an interger!")
                    print('*' * 10)
            else:
                print("Only available options are 1 or 2 or 3, please re-enter it!")
