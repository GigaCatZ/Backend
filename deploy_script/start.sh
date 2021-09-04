#!/bin/bash                                                                                                                                                                     

docker run -d --name backend \
     --link iccourses \
     -e TZ=Asia/Bangkok \
     -v /home/lolcat/Backend/:/usr/src/app/ \
     backend

