import streamlit as st
import pandas as pd
import numpy as np
import cv2
import psutil
import subprocess
import threading
import time
import shutil

import depthai as dai

st.set_page_config(page_title='Record Video', layout='centered')

online = st.sidebar.checkbox("Initialise camera")
select_folder = st.sidebar.checkbox("Select folder to use")


stframe = st.empty()




@st.cache(allow_output_mutation=True)
def get_map():
    print("obtained a new copy of imshow_map")
    return {}

global_dict = get_map()

show_map = get_map()
out_map = get_map()




# set up folder
select_state_cam = st.sidebar.selectbox("Select state of cam",
                                ['static', 'dynamic'])
num_folder = st.sidebar.slider("Select folder number", max_value=10, min_value=1, step=1)
folder_path = "/home/haoxuan362709/streamlit_file"
folder_name = folder_path + "/" + str(select_state_cam) + "_" + str(num_folder)
try:
    subprocess.run(['mkdir', folder_name])
except:
    st.write = folder_name + " " + "exists"





# Initialise pipeline

dev = None
outQ_B = None
showQ_B = None

file_camb_H264 = None

@st.experimental_singleton
def initialize_depthai():

    print("Initialise Device")

    # Create pipeline
    pipeline = dai.Pipeline()

    # Define 
    #source
    monoB = pipeline.create(dai.node.MonoCamera)
    #encoder
    veB = pipeline.create(dai.node.VideoEncoder)
    #output
    veBOut = pipeline.create(dai.node.XLinkOut)

    veBOut.setStreamName('veBOut')
    #display
    manipB = pipeline.create(dai.node.ImageManip)
    manipOutB = pipeline.create(dai.node.XLinkOut)

    manipOutB.setStreamName("manipBOut")

    # Properties
    #source
    monoB.setBoardSocket(dai.CameraBoardSocket.CAM_B)
    monoB.setFps(30)
    #encoder
    veB.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H264_MAIN)
    #display
    monoB.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
    manipB.setMaxOutputFrameSize(monoB.getResolutionHeight()*monoB.getResolutionWidth()*3)

    # Linking
    #source -> encoder
    monoB.out.link(veB.input)
    #encoder -> output
    veB.bitstream.link(veBOut.input)
    #source -> manip
    monoB.out.link(manipB.inputImage) 
    #manip -> display
    manipB.out.link(manipOutB.input)

    dev = dai.Device(pipeline)

    #output queue : store data from output 
    outQ_B = dev.getOutputQueue(name=veBOut.getStreamName(), maxSize=30, blocking=False)
    #display queue : 
    showQ_B = dev.getOutputQueue(name=manipOutB.getStreamName(), maxSize=4,blocking=False)

    def out_callback():
        # print(global_dict["recording_state"])
        if( global_dict["recording_state"]):
            file_camb_H264 = open((folder_name + '/record.h264'), 'wb')
            print("I am recording")
            outQ_B.get().getData().tofile(file_camb_H264)
        else:
            print("i am not recording")
            pass


    def show_callback():
        show_map["mono8"] = showQ_B.get().getCvFrame()

    outQ_B.addCallback(out_callback)
    showQ_B.addCallback(show_callback)

    return dev, outQ_B, showQ_B





dev, outQ_B, showQ_B = initialize_depthai()
print("depthai set up.")


if online and select_folder:
    print('Webcam Online ...')
      
    # st.write(st.session_state)

    print("Recording start.")
    print("Press Ctrl+C to stop recording...")

    global_dict["recording_state"] = st.checkbox('Record video')



    while True:

        # print(f"current_state = {global_dict["recording_state"]}")
        if "mono8" not in show_map:
            continue
        stframe.image(show_map["mono8"],channels = 'RGB', use_column_width=True)



        







                        

