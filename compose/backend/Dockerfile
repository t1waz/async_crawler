FROM python:3

WORKDIR /app

RUN mkdir /manage

RUN mkdir /entrypoint

COPY ./requirements.txt /app

COPY ./compose/backend/entrypoint.sh /entrypoint
RUN chmod +x /entrypoint/entrypoint.sh

RUN pip install --upgrade pip \
	&& pip install -r /app/requirements.txt

ENTRYPOINT ["/entrypoint/entrypoint.sh"]