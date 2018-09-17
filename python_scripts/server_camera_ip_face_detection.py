from flask import Flask, Response
import cv2
import imutils
import face_recognition


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture("http://192.168.1.143:4747/mjpegfeed?640x480")
        self.i = 0

    def __del__(self):
        self.video.release()

    def process_frame(self, frame):
        self.i += 1
        if self.i % 2 == 0:
            print(self.i)
            # convert the input frame from BGR to RGB then resize it to have
            # a width of 750px (to speedup processing)
            # rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # rgb = imutils.resize(rgb, width=750)
            # r = frame.shape[1] / float(rgb.shape[1])
            r = 1
            rgb = frame

            # detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input frame, then compute
            # the facial embeddings for each face
            boxes = face_recognition.face_locations(rgb, model="hog")
            for (top, right, bottom, left) in boxes:
                # rescale the face coordinates
                top = int(top * r)
                right = int(right * r)
                bottom = int(bottom * r)
                left = int(left * r)

                # draw the predicted face name on the image
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        return frame

    def get_frame(self):
        # Read frame
        success, frame = self.video.read()
        frame = self.process_frame(frame)
        ret, jpeg = cv2.imencode('.jpg', frame)

        return jpeg.tobytes()

app = Flask(__name__)


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


app.run(host='0.0.0.0', port=8080, debug=True)