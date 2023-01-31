import streamlit as st
import subprocess

st.set_page_config(page_title='Training', page_icon='./media/vilota.jpg', layout='centered')

text_kpi, num_kpi = st.columns(2)
with text_kpi:
    yv5_path = st.text_input("Insert path to yolov5", '/home/user/yolov5')
    yv5_data = st.text_input('Insert dataset yaml file', './data.yaml')
    yv5_weights = st.text_input('Insert yolov5 pretrained weights', 'yolov5n.pt')

go_2_path = 'cd ' + yv5_path

with num_kpi:
    yv5_image_width = st.number_input('Insert image size', min_value=0, max_value=1280, value=640, step=32)
    yv5_batch = st.number_input('Insert batch size', min_value=0, max_value=128, value=64, step=8)
    yv5_epoch = st.number_input('Insert epochs', min_value=0, max_value=1000, value=500, step=10)

yv5_rect = st.checkbox('Rectangular training?')
if yv5_rect:
    rect = ' --rect '
else:
    rect = ' '
    
yv5_workers = st.number_input('Insert no. of workers', min_value=0, max_value=4, value=2, step=1)
train_code = 'python3 train.py' + ' --img ' + str(yv5_image_width) + ' --batch ' + str(yv5_batch) + ' --epoch ' + str(yv5_epoch) + ' --data ' + yv5_data + ' --weights ' + yv5_weights + str(rect) + '--workers ' + str(yv5_workers)
img_width = ' --img ' + str(yv5_image_width)
batch = ' --batch ' + str(yv5_batch)
epochs = ' --epoch ' + str(yv5_epoch)
dataset = ' --data ' + yv5_data
weights = ' --weights ' + yv5_weights
rectangle = str(rect)
workers = '--workers ' + str(yv5_workers)

st.code(go_2_path)
st.code(train_code)
def subproc(clicked):
    st.subheader(clicked)
train = st.button('Train', on_click=subproc, args=("**Training...**",))

if train:
    subprocess.run(["sh", "train.sh", yv5_path, img_width, batch, epochs, dataset, weights, rectangle, workers])
    st.info(":information_source: Results saved to " + yv5_path + "/train/exp...")
    st.success(':white_check_mark: Trained')