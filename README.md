# leDora

This repository contains the source code for the leDora project.

The leDora project is a software application designed to assist professionals in improving the reading
skills of dyslexic children. Dyslexia is a learning disorder that affects reading, spelling, and writing 
abilities. This project aims to provide a supportive environment for dyslexic children to enhance their 
reading skills through targeted exercises and interactive learning methods.

This preliminary version of the leDora project is a gaming application that uses a series of exercises
that aim to speed up the reading process and improve the reading skills of dyslexic children.

The game session must be overseen and operated  by a professional who can monitor the child's progress.

## How it was implemented

The main script is called [ledora.py](ledora.py) and it is implemented using the pygame library.
it provides interactive features for users to practice reading words in different languages and types.

Let's break down what the code does:

1. Imports: The script imports various modules such as sys, os, pygame, pyphen, time, datetime, random, re, and pyperclip to facilitate different functionalities of the program.

2. Constants and Configuration: It sets up various constants like the path to assets, word duration, application name, version, font color, and logo file. It also initializes the environment variable 'SDL_VIDEO_CENTERED' to center the game window on the screen.

3. Words Mapping: This dictionary WORDS_MAPPING contains mappings for different languages and types of words (frequent or hard) along with their associated properties.

4. Helper Functions: It defines several helper functions like resource_path, asset_item_path, and get_font to facilitate resource management, especially for fonts and assets.

5. Button Class: This class defines a customizable button for the GUI interface of the program. It manages the button's appearance, position, and interaction.

6. Ledora Class: This is the main class of the program. It manages the game state, initializes pygame, sets up the screen, handles user input, and controls the flow of the program. 

7. Main Function: It creates an instance of the Ledora class and starts the game by calling the screen_initial method.

## How to install the application

The application is currently available as a exe file that can be accessed using the following link:

TODO: Add link to the application

## Preparing the local environment for development

### 1. Install Python

If Python is not already installed on your system, download and install Python from the official Python website. 
Ensure that you select the option to add Python to your system's PATH during installation.

### 2. Create a Virtual Environment

Navigate to the root directory of the project in your terminal or command prompt. Then, follow these steps to 
create a Python virtual environment:

```shell
# Navigate to the project directory
cd ledora

# Create a virtual environment named 'env'
python -m venv env
```

### 3. Activate the Virtual Environment

Activate the virtual environment by running the appropriate command for your operating system:

On Windows:

```shell
.\env\Scripts\activate
```

On macOS and Linux:

```shell
source env/bin/activate
```

### 4. Install Dependencies

Once the virtual environment is activated, install the required dependencies using the pip package manager and the provided requirements.txt file:

```shell
pip install -r requirements.txt
```


### 5. Verify Installation

To verify that the installation was successful, you can run the following command to display the installed packages along with their versions:

```shell
pip list
```

### 6. Deactivate the Virtual Environment

Once you have finished working with the project, you can deactivate the virtual environment by running the following command:

```shell
deactivate
```

## How to run the application



## How to build the application

To build the application, you can use the `pyinstaller` package to create a standalone executable file.

```shell
pyinstaller ledora.spec
```

or 

```shell
pyinstaller --onefile --noconsole --add-data "assets;assets" --add-data "txts;txts" --add-data "external;external" ledora.py
```


