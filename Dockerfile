FROM python:3.9
ENV PYTHONUNBUFFERED 1

# Create a directory for the app
RUN mkdir /Flask-Web-chat

# Copy the requirements file and install dependencies
COPY ./requirements.txt /Flask-Web-chat/requirements.txt

# switch working directory
WORKDIR /Flask-Web-chat

RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the code to the container
COPY . /Flask-Web-chat

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["main.py" ]