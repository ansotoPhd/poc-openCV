from .base_handler import BaseHandler


class ImageHandler(BaseHandler):

    def data_received(self, chunk):
        pass

    def prepare(self):
        self.image_service = self.settings['opencv_service']

    def get(self, img_number=None, face_number=None, **kwargs):
        print("Image number: " + str(img_number))
        print("Face number: " + str(face_number))
        method = self.get_argument("method", None, True)

        try:
            image_base64, n_faces, method = self.image_service.proccess_image(
                int(img_number), 600, 800, method)
            self.finish(
                self.render_template("images.html",
                                     **dict(
                                         n_faces=n_faces,
                                         image=image_base64,
                                         method=method
                                     )))
        except Exception as e:
            print("Exeption" + str(e))
            self.write(str(e))


