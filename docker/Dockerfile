FROM python:3.7.3-stretch

# copy entire app into the image
COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# create a seperare user to run this application
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

#copy codebase within app
COPY . /opt/app

# run it!
CMD [ "python", "src/MetProWorkflowApp.py" ]


