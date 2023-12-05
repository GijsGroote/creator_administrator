"""
Communicate with Student Assistant (SA).
"""

import sys

def choose_one_option(question: str, options: list, options_type=" ") -> str:
    """ Ask SA choose one option. """

    options = {option_number+1: option for (option_number, option) in enumerate(options)}

    while True:
        print(question)
        for key, value in options.items():
            if key == 1:
                print(f'{key}. {value} (default)')
            else:
                print(f'{key}. {value}')

        if len(options) == 0:
            choice = input(f'Enter {options_type}: ')
        else:
            choice = input(f'Input a number or new {options_type}:')

        if len(options) == 0:
            return str(choice).lower()
        
        if str(choice) == '' and len(options) > 0:
            return str(options[1])
        
        try:
            choice_int = int(choice)

            if choice_int in range(1, len(options)+1, 1):
                return str(options[choice_int])
            else:
                print(f'{choice_int} is not in {range(1, len(options)+1, 1)}, try again')
                continue
        except Exception:
            return str(choice).lower()

def choose_option(question: str, options: list) -> list:
    """ Ask SA to select/deselect a number of options. """

    options = {option_number+1: [False, option] for (option_number, option) in enumerate(options)}

    while True:
        print(question)
        for key, value in options.items():
            status = '[X]' if value[0] else '[ ]'
            print(f"{key}. {status} {value[1]}")

        choice = input("Enter number to select/deselect (or 'q' to quit): ")

        if choice == 'q':
            break

        try:
            choice_int = int(choice)
        except:
            print(f'could not convert {choice} to a number, try again')
            continue

        if choice_int in options:
            options[choice_int][0] = not options[choice_int][0]
        else:
            print(f'{choice_int} should be in range [1, {len(options)}], try again')

    return [value[1] for (key, value) in options.items() if value[0]]

def yes_or_no(question: str) -> bool:
    """ Ask SA to answer question with yes (True) or no (False). """
    answer = input(question)

    if answer in ["n", "N", "nee", "NEE"]:
        return False
    return True

def password_please(gv: dict):
    """ input password to continue python process """
    attempt = 1
    while attempt <= 3:
        password_given = input('Enter password:')
        if password_given == gv['PASSWORD']:
            print('password correct')
            return
        print(f'password: {password_given} is incorrect')
        attempt += 1

    print('3 incorrect attempts, abort. . .')
    sys.exit(0)
