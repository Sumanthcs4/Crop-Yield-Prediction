from setuptools import find_packages, setup
from typing import List

def get_requirements()->List[str]:
    requirement_lst:List[str]=[]
    """
    This function will return the list of requirements
    """
    try:
        with open('requirements.txt') as file:
            #Read lines fromm the file
            lines = file.readlines()
            # Process each linne
            for line in lines:
                requirement = line.strip()
                #ignore the empty lines and -e .
                if requirement and requirement!= '-e .':
                    requirement_lst.append(requirement)
                    
    except FileNotFoundError:
        print("requirements.txt file not found. Please create it with the required packages.")
        
    return requirement_lst

setup(
    name = "Crop-Yield-Prediction",
    version = "0.0.1",
    author= "Sumanth C S",
    email = "ssumanth510@gmail.com",
    packages= find_packages(),
    install_requires = get_requirements(),
)