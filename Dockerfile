FROM python:3.7.4-stretch

RUN apt-get -y update

# Google Chrome dependencies
RUN apt-get install -y libasound2 libatk-bridge2.0-0 libatspi2.0-0 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libxkbcommon0 libxshmfence1 xdg-utils fonts-liberation

# Google Chrome (specific version)
RUN wget -O /tmp/google-chrome-stable_current_amd64.deb https://www.slimjet.com/chrome/download-chrome.php?file=files%2F90.0.4430.72%2Fgoogle-chrome-stable_current_amd64.deb
RUN dpkg -i /tmp/google-chrome-stable_current_amd64.deb && rm /tmp/google-chrome-stable_current_amd64.deb

# ChromeDriver (specific version)
ADD https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_linux64.zip /opt/chrome/
RUN cd /opt/chrome/ && unzip chromedriver_linux64.zip

# Japanese font
ENV LANGUAGE ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
RUN apt-get install -y --no-install-recommends locales && \
    locale-gen ja_JP.UTF-8 && \
    apt-get install -y --no-install-recommends fonts-ipafont

# python packages
ADD requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

# Add source files
WORKDIR /app
ADD *.py /app
ADD lib /app
ADD jobcan_auto_input.sh /app
