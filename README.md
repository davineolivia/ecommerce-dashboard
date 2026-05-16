# E-Commerce Public Dataset Dashboard

## Setup Environment - Anaconda
conda create --name main-ds python=3.10
conda activate main-ds
pip install -r requirements.txt

## Setup Environment - Shell/Terminal
mkdir submission
cd submission
pipenv install
pipenv shell
pip install -r requirements.txt

## Run Streamlit App
cd dashboard
streamlit run dashboard.py