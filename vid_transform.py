import cv2
import sys, time, os, argparse
import vid_read as vid_read

def frame_transform_complex(frame, trans_complex):
    if trans_complex == True:
        #frame = trans_complex(frame)
        #frame = super_res(frame)
        pass
        #return frame
    
def frame_transform_simple(frame, width_new, height_new):
    dim = (width_new, height_new)
    frame = cv2.resize(frame, dim, interpolation=cv2.INTER_CUBIC)
        
    return frame

def frame_write(cap, out, f_ow, f_nw, out_dir, resize, width_new, height_new, trans_complex=False):
    
    i=0
    time_read_frame_cum = 0
    time_transform_cum = 0
    if trans_complex == True:
        resize=False

    while(cap.isOpened()):
        time_read_frame_start = time.time()
        ret, frame = cap.read()
        if ret == False:
            break
        time_read_frame_end = time.time()
        time_read_frame_cum += time_read_frame_end - time_read_frame_start
        if f_ow != False:
            cv2.imwrite(os.path.join(out_dir, '{}_old.png'.format(i)), frame)
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        time_transform_start = time.time()
        if resize == True:
            frame = frame_transform_simple(frame, width_new, height_new)
        elif trans_complex == True:
            #frame = frame_transform_complex(frame)
            pass
        time_transform_end = time.time()
        time_transform_cum += time_transform_end - time_transform_start

        #frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame)
        if f_nw != False:
            cv2.imwrite(os.path.join(out_dir, '{}_new.png'.format(i)), frame)

        if (i%100==0):
            print('Added frame: ', i) 
        i += 1
        
    return time_read_frame_cum, time_transform_cum, i 
    

def vid_transform(vid_path, f_ow, f_nw, width_new, height_new, fps_new, codec_new, trans_complex):
    time_start = time.time()
    vid_name, cap, width, height, fps = vid_read.vid_read(vid_path)
    
    if width_new == False:
        width_new = width
        resize = False
    else:
        resize = True
        resize = False
    if height_new == False:
        height_new = height
    else:
        resize = True
    if fps_new == False:
        fps_new = fps
    codec_new = tuple(char.upper() for char in codec_new)
        
    out_dir = 'results'
    os.makedirs(out_dir, exist_ok=True)
    out_name = os.path.join(out_dir, '{}_trans.avi'.format(vid_name)) 

    out = cv2.VideoWriter(out_name, cv2.VideoWriter_fourcc(codec_new[0], codec_new[1], codec_new[2], codec_new[3]), fps_new, (width_new, height_new)) #lossy but works
        
    print('Started transforming frame by frame from video.')
    time_read_frame_cum, time_transform_cum, i = frame_write(cap, out, f_ow, f_nw, out_dir, resize, width_new, height_new, trans_complex)
    print('Finished transforming video.')
    cap.release()
    out.release()
    
    return time_start, time_read_frame_cum, time_transform_cum, i

def times(time_start, time_read_frame_cum, time_transform_cum, i):
    
    time_end = time.time()
    time_total = time_end - time_start
    print('Total time {} s. Avg/frame: {} s.'.format(str(time_total), str(time_total/i)))
    time_read_frame_avg = time_read_frame_cum/i
    print('Total time spent reading frames {} s. Avg/frame: {} s.'.format(time_read_frame_cum, time_read_frame_avg))
    time_transform_avg = time_transform_cum/i
    print('Total time spent processing frames {} s. Avg/frame: {} s.'.format(time_transform_cum, time_transform_avg))
    
def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', required=True, dest='input', type=str, help='Input video path.')
    parser.add_argument('-cc', required=False, dest='cc', type=str, default='MJPG', help='Change FourCC codec of video. Def = MJPG')
    parser.add_argument('-f_ow', required=False, dest='f_ow', type=bool, default=False, help='Save original frames. Def dont use and it wont save any frames.')
    parser.add_argument('-f_nw', required=False, dest='f_nw', type=bool, default=False, help='Save processed frames. Def dont use and it wont save any frames.')
    parser.add_argument('-w', required=False, dest='w', type=int, default=False, help='Change width of video. Def = False, and use original width.')
    parser.add_argument('-ht', required=False, dest='h', type=int, default=False, help='Change height of video. Def = False, and use original height.')
    parser.add_argument('-fps', required=False, dest='fps', type=float, default=False, help='Change FPS of video. Def = False, and use original FPS.')
    parser.add_argument('-trans', required=False, dest='trans', type=str, default=False, help='Add any other non-standard transform. Def = False.')
    
    args = parser.parse_args()
    print(args)
    
    time_start, time_read_frame_cum, time_transform_cum, i = vid_transform(args.input, args.f_ow, args.f_nw, args.w, args.h, args.fps, args.cc, args.trans)
    times(time_start, time_read_frame_cum, time_transform_cum, i)
    
main()