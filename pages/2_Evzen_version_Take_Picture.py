#https://github.com/vilota-dev/yolov5_workflow/blob/master/streamlit/pages/2_Take_Picture.py
import streamlit as st
import numpy as np
import cv2
import psutil
import subprocess
import os, signal
from time import time

import capnp
import ecal.core.core as ecal_core
from byte_subscriber import ByteSubscriber
capnp.add_import_hook(['./thirdparty/ecal-common/src/capnp'])
import image_capnp as eCALImage
import detection2d_capnp as eCALDetection2d

st.set_page_config(page_title='Take picture', page_icon='./media/vilota.jpg', layout='centered')

def findProcessIdByName(processName):
    listOfProcessObjects = []
    #Iterate over the all the running process
    for proc in psutil.process_iter():
       try:
           pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
           # Check if process name contains the given name string.
           if processName.lower() in pinfo['name'].lower() :
               listOfProcessObjects.append(pinfo)
       except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess) :
           pass
    return listOfProcessObjects
        
@st.cache(allow_output_mutation=True)
def get_imshow_map():
    print("obtained a new copy of imshow_map")
    return {}

imshow_map = get_imshow_map()

@st.experimental_singleton
def initialise_ecal(name):
    def callback(topic_name, msg, ts):
        with eCALImage.Image.from_bytes(msg) as imageMsg:

            if (imageMsg.encoding == "mono8"):
                mat = np.frombuffer(imageMsg.data, dtype=np.uint8)
                mat = mat.reshape((imageMsg.height, imageMsg.width, 1))
                imshow_map["mono8"] = mat

            elif (imageMsg.encoding == "yuv420"):
                mat = np.frombuffer(imageMsg.data, dtype=np.uint8)
                mat = mat.reshape((imageMsg.height * 3 // 2, imageMsg.width, 1))
                mat = cv2.cvtColor(mat, cv2.COLOR_YUV2BGR_IYUV)
                imshow_map["yuv420"] = mat
            else:
                raise RuntimeError("unknown encoding: " + imageMsg.encoding)

    # print eCAL version and date
    print("eCAL {} ({})\n".format(ecal_core.getversion(), ecal_core.getdate()))
    # initialize eCAL API
    ecal_core.initialize([], name)
    # set process state
    ecal_core.set_process_state(1, 1, "I feel good")
    # create subscriber and connect callback
    sub = ByteSubscriber("S0/camc")
    sub.set_callback(callback)

initialise_ecal("test_image_sub_st")

online = st.sidebar.checkbox("Initialise camera")

if 'count' not in st.session_state:
    st.session_state.count = 0
def increment_counter():
    st.session_state.count += 1

previous = 0
stframe = st.empty()
vk = "/home/haoxuan362709/git/oak_camera_driver/build/oak_camera_driver "
json = "/home/haoxuan362709/git/oak_camera_driver/config/4cam.json"
vkjson = vk + json

select_folder = st.sidebar.checkbox("Select folder to use")

if online == False:
    listOfProcessIds = findProcessIdByName('oak_camera_driver')
    if len(listOfProcessIds) > 0:
        print('Process Exists | PID and other details are')
        for elem in listOfProcessIds:
            processID = elem['pid']
            os.kill(processID, signal.SIGKILL)
            print("stopped camera driver")
if online and select_folder:
    camRun = subprocess.Popen(vkjson, shell=True)

    select_state_cam = st.sidebar.selectbox("Select state of cam",
                                    ['static', 'dynamic'])
    num_folder = st.sidebar.slider("Select folder number", max_value=10, min_value=1, step=1)
    folder_path = "./output"
    folder_name = folder_path + "/" + str(select_state_cam) + "_" + str(num_folder)
    try:
        subprocess.run(['mkdir', folder_name])
    except:
        st.write = folder_name + " " + "exists"

    taking_pics = st.button('Take 1 pic', on_click=increment_counter)
    print('Webcam Online ...')
    while ecal_core.ok():
        # Webcam feed
        if "mono8" not in imshow_map:
            continue
        right_mono = imshow_map["mono8"]
        right_rgb = cv2.cvtColor(right_mono, cv2.COLOR_GRAY2RGB)
        vk_height, vk_width, vk_channels = right_rgb.shape
        stframe.image(right_rgb,channels = 'RGB', use_column_width=True)

        if taking_pics and st.session_state.count > previous:
            img_name = folder_name + "/Frame_{}.jpg".format(st.session_state.count)
            cv2.imwrite(img_name, right_rgb)
            print("{} written!".format(img_name))
            st.success(':white_check_mark: {} written!'.format(img_name))
            previous = st.session_state.count

        listOfProcessIds = findProcessIdByName('oak_camera_driver')
        if len(listOfProcessIds) > 1:
            print('Process Exists | PID and other details are')
            process = listOfProcessIds[1]
            processID = process['pid']
            os.kill(processID, signal.SIGKILL)
            print("stopped camera driver")
        
    ecal_core.finalize()