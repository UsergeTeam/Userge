# Docker Guide For Userge 🐳 #

## Install docker ##
- Follow the official docker [installation guide](https://docs.docker.com/engine/install/ubuntu/)

## Install Docker-compose ##
- Easiest way to install docker-compose is <br>
```sudo pip install docker-compose```
- Also you can check other official methods of installing docker-compose [here](https://docs.docker.com/compose/install/)

## Run Userge ##
- We dont need to clone the repo (yeah Docker-compose does that for us)
- Setup configs
    - Download the sample config file <br>
        - ```mkdir userge && cd userge```
        - ```wget https://raw.githubusercontent.com/UsergeTeam/Userge/alpha/config.env.sample -O config.env```
        - ```vim config.env```
    - Download the yml file for docker-compose
        - ```wget https://raw.githubusercontent.com/UsergeTeam/Userge/alpha/resources/docker-compose.yml```
- Finally start the bot <br>
```docker-compose up -d```
- The bot should be running now <br>
Check logs with ```docker-compose logs -f```

## How to stop the bot ##
- Stop Command
    ```docker-compose stop```
    - This will just stop the containers. Built images won't be removed. So next time you can start with ``docker-compose start`` command <br>
    And it won't take time for building from scratch<br>
    
- Down command
    ```docker-compose down```
    - You will stop and delete the built images also. So next time you have to do ``docker-compose up -d`` to start the bot<br>
    
### Q&A ###
- How to see logs <br>
    `docker-compose logs -f`
- How to update <br>
    `docker-compose up -d` <br>
    Changes will be fetched from git repo. You can change repo url from _docker-compose.yml_ file