from PIL import Image, ImageTk

import constants

class Sprite(constants.correction):
    def rotate_sprite(self, angle):
        g = constants.grid_size
        cx = self.column
        cy = self.row
        img = self.img.convert('RGBA')
        rotated_image = img.rotate(angle, expand=True)
        self.sprite = ImageTk.PhotoImage(rotated_image)
        canvas = self.canvas
        canvas.delete(self.canvas_sprite)
        self.canvas_sprite = canvas.create_image(((cx+0.5)*g)+5, ((cy+0.5)*g)+5, image=self.sprite)

    def on_clock_tick(self, tick):
        pass

    def on_hour_tick(self, hour):
        pass

    def on_day_tick(self, day):
        pass

    def on_month_tick(self, month):
        pass

    def on_year_tick(self, year):
        pass