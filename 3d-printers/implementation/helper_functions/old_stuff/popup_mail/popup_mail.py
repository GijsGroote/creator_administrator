
import os
import subprocess


def main():

    filename = 'gijs.eml'
    print(f"opening {filename}")
    # os.system("start " + filename)


    subprocess.run(['open', filename], check=True)

    print(f"done")




if __name__ == '__main__':
    main()
