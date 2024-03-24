---
sidebar_position: 1
---

# Install Creator Administator


Get started by **cloning the repository**, Open the CMD and paste the following:

```bash
git clone git@github.com:GijsGroote/creator_administrator.git
```

Make sure that the following programs are present on your machine.

- [python](https://www.python.org/downloads/) version 3.10 or 3.11
- [poetry](https://python-poetry.org/docs/) version 1.8.2 or above
- [Outlook](https://microsoft-outlook.en.softonic.com/?ex=RAMP-1768.2) the 2019 version


## Install the dependencies with Poetry

Change directory to the github repository folder:

```bash
cd creator_administrator
```

Create a new Poetry environment and install the dependencies for Creator Administartor:

```bash
poetry install
```

Enter the Poetry environment:

```bash
poetry shell
```

## Run a Python main file

There are two main files, one that starts the 3D print application and one that starts the laser cut application.

To start the 3D print application, run:
```bash
python creator_administrator/printer/src/printer_app.py 
```

To start the laser cut application, run:
```bash
python creator_administrator/laser/src/laser_app.py 
```

You'll see a short message: ___tracker file created___, (you can press ok)

Then, Creator administrator should appear.


Creator Administartor, 3D print application:

![Docusaurus logo](/img/printer_app.png)

Creator Administartor, laser cut application:

![Docusaurus logo](/img/laser_app.png)

