import torch
import shutil
import matplotlib.pyplot as plt
import matplotlib
import torchvision
import cv2
import glob

def run_yolo(model,image_path,Choosen_Id,face_id):
    results = model(image_path)
    try:
        shutil.rmtree('runs')
    except Exception:
        pass

    output_yolo_image_shape = results.ims[0].shape
    mid_point = output_yolo_image_shape[1]//2 #600

    captured = results.pandas().xyxy[0]

    image,annotation_list = cv2.imread(image_path),[]
    for i,c in enumerate(captured['class']):
        r = captured['name'][i]
        if c == Choosen_Id:
            r = "Driver Use" if captured.iloc[i].xmin > mid_point else "Passenger Use"
        
        elif c == face_id:
            r = "Driver" if captured.iloc[i].xmin > mid_point else "Passenger"
            
        #(np.random.randint(255),np.random.randint(255),np.random.randint(255))
        color_list = {"Driver":(125,46,34),
                      "Passenger":(234,99,123),
                      "Driver Use":(0,0,255),
                      "Passenger Use":(0,255,0),
                      "Cell Phone Attached":(0,255,0),
                      "Hand":(166,124,99),
                      "OOD":(10,10,10),
                      }
        
        image = cv2.rectangle(image, 
                             (int(captured.iloc[i].xmin),int(captured.iloc[i].ymin)), 
                             (int(captured.iloc[i].xmax),int(captured.iloc[i].ymax)),
                             color_list[r], 4)
        image = cv2.putText(image,r,
                           (int(captured.iloc[i].xmin),int(captured.iloc[i].ymin)),
                           cv2.FONT_HERSHEY_SIMPLEX,1.2, color_list[r], 3)
        
        annotation_list.append(r)

    output = 1 if "Driver Use" in annotation_list else 0

    results.save()
    
    return image, output 
    

    
r"""
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

CIH__id = 0#1

#model = torch.hub.load(r"C:\Users\hp\OneDrive - University of Ottawa\Desktop\RAVEN ALL\NEW STUDY\yolov5", 'custom', path=r"C:\Users\hp\OneDrive - University of Ottawa\Desktop\RAVEN ALL\NEW STUDY\yolov5\models\new_yolo.pt", source='local') 
model = torch.hub.load(r"C:\Users\hp\OneDrive - University of Ottawa\Desktop\RAVEN ALL\NEW STUDY\yolov5", 'custom', path=r"C:\Users\hp\OneDrive - University of Ottawa\Desktop\RAVEN ALL\NEW STUDY\yolov5\models\new_yolo.pt", source='local') 

#model = model.to(device)

img_p = "captured.jpg"

images = [file for file in glob.glob('Detected\*.jpg')]
print(images,len(images))
for index,i in enumerate(images):
    image, output = run_yolo(model,i,CIH__id)
    output = "not Usage" if output == 0 else "usage"
    #cv2.putText(image,output)
    cv2.imwrite(r"C:\Users\hp\OneDrive - University of Ottawa\Desktop\RAVEN ALL\NEW STUDY\Detected\{}_{}_result.jpg".format(output,index),image)



plt.ion()


matplotlib.use('TkAgg') # Change backend after loading model
 
#plt.imshow(image)

#plt.pause(0.5)
plt.show()
"""











