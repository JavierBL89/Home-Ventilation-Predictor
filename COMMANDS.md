Check Python Virtual Environment:

1. Ensure you're in a virtual environment. If you haven't created one, create it:
bash

   - python3.10 -m venv venv   (VERSION 10 NEEDED, not 13)

2. Activate the virtual environment:

   - source venv/bin/activate

3. Install Dependencies from requirements.txt:
Install all the dependencies listed in your requirements.txt file:

   - pip freeze > requirements.txt

   - pip install -r requirements.txt


This will install Flask and all other required packages.
Verify Installation:
Check if Flask is installed:

   - pip show flask

   - pip install flask

If Flask or other packages are missing, ensure the requirements.txt file is correctly formatted and retry the installation.
Run the Application:

After installing the dependencies, run the server:

   - python3 server.py


Common Errors:

If you still encounter a ModuleNotFoundError, ensure the virtual environment is activated (source venv/bin/activate) and that the installation commands were run inside the activated environment.
Check the Python version being used:

   - python3 --version


Install dependencies
   
   - pip install --upgrade pip

   - pip install --upgrade pip setuptools wheel numpy cython

   - pip install numpy cython pystan==2.19.1.1

   - pip install prophet

   - pip install pandas matplotlib statsmodels seaborn scikit-learn tensorflow pmdarima

PYTORCH

   - pip install torch
   - pip install tensorflow

- install PyTorch
   - pip install torch torchvision torchaudio

   Verify Installation
   - python -c "import torch; print(torch.__version__)"

Install compatible keras
   pip install tf-keras

Install datasets
   - pip install datasets

    ##  pip install torch tensorflow datasets tf-keras 'transformers[torch]'
  If Installation Fails
     Ensure your Python version is compatible (3.8 or later is recommended).
     Use an alternate package index in case of connection issues:

     - pip install datasets --index-url https://pypi.org/simple

"Using the `Trainer` with `PyTorch` requires `accelerate>=0.26.0`
Please run `pip install 'transformers[torch]'` or `pip install 'accelerate>=0.26.0'`",