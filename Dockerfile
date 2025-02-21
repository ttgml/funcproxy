FROM python:3.12.9-bookworm

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
COPY src /app/src
WORKDIR /app/src
EXPOSE 7777
CMD ["python", "-m", "funcproxy.cli"]