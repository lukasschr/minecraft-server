FROM ubuntu:24.04

RUN apt-get update && apt-get upgrade -y

# Basic's
RUN apt install -y wget curl

# Pufferpanel 3.0.0-rc.13
RUN curl -s https://packagecloud.io/install/repositories/pufferpanel/pufferpanel/script.deb.sh?any=true | bash && \
    apt-get update && \
    apt-get install -y pufferpanel=3.0.0-rc.13

# Java 21
RUN wget -O - https://apt.corretto.aws/corretto.key | gpg --dearmor -o /usr/share/keyrings/corretto-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/corretto-keyring.gpg] https://apt.corretto.aws stable main" | tee /etc/apt/sources.list.d/corretto.list && \
    apt-get update && \
    apt-get install -y java-21-amazon-corretto-jdk

# Initialize (Guter Pfusch)
RUN mkdir -p /var/lib/pufferpanel/config && \
    mkdir -p /etc/pufferpanel && \
    timeout 5 pufferpanel run || true && \
    mv /etc/pufferpanel/config.json /var/lib/pufferpanel/config/config.json && \
    ln -sf /var/lib/pufferpanel/config/config.json /etc/pufferpanel/config.json

CMD ["pufferpanel", "run"]