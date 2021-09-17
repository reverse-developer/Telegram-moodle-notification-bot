FROM fedora

RUN sudo dnf -y update && \
    sudo dnf -y install make wget gcc firefox Xvfb 

RUN wget http://download.redis.io/redis-stable.tar.gz && \
    tar xvzf redis-stable.tar.gz && \
    sudo make install -C redis-stable

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz && \
    tar -xvzf geckodriver* && \
    chmod a+x geckodriver && \ 
    mv geckodriver /usr/local/bin/

RUN useradd -ms /bin/bash moodle

ADD . /usr/local/bin/
RUN chmod a+x /usr/local/bin/entry-point.sh 

RUN pip3 install python-telegram-bot redis selenium walrus pyvirtualdisplay 

USER moodle
ENTRYPOINT [ "./usr/local/bin/entry-point.sh" ]
