# overview of this project

This is a python script that allows you convert your video into a .gif file on your local machine

# how to run

1. clone this repo on your local machine
2. navigate to the root folder of the downloaded repo
3. run the following command to setup the project and ensure you have python 3 installed

```
pip install -r requirements.txt
```
4. Place your videos in the videos folder of the project then run this command 

```
python convert.py 
```

Check the gifs folder for an output of your .gifs

Project structure

/videos
You can place as your .mov, .xyz and .vis videos that you want converted here. 

/gifs
this is where your .gifs will be available once you've run the convert.py script. 

convert.py

This is a file that will use ffmpeg (an open source tool) to convert the files

requirements.txt 

This is the requirements file that installs the right open source dependencies that you need

# limitations

This project uses Python with `imageio-ffmpeg` (a pip-installed ffmpeg binary). I thought this would be easier for people to get started with because it just requires the user to install the requirements.txt but, there are obviously tradeoffs with this approach since its not the "pure" version of ffmpeg. 

# optional flags


ffmpeg has many flags you can add  to convert the files in the way you want. For example, you can pass extra ffmpeg flags to change frames per second like this:

```
python convert.py --ffmpeg-args "-ss 0 -t 5"
```

See the full list of ffmpeg flags when converting videos to gifs here: https://ffmpeg.org/ffmpeg.html#Options 