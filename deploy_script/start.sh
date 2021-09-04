#!/bin/bash                                                                                                                                                                     

docker run -d --name backend \
     --link iccourses \
     -v /home/lolcat/Backend/:/usr/src/app/ \
     backend

