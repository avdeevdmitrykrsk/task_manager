FROM python:3.9

WORKDIR /app

RUN apt update && \
    apt install -y netcat-traditional curl && \
    apt clean autoclean && apt autoremove --yes

COPY . .

RUN pip install -r requirements.txt --no-cache-dir

RUN sed -i 's/\r$//' entrypoint.bash && \
    chmod +x entrypoint.bash

CMD ["/bin/bash", "entrypoint.bash"]